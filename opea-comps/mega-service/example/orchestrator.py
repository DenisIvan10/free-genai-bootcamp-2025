# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import asyncio
import contextlib
import copy
import json
import os
import re
import threading
import time
from typing import Dict, List

import aiohttp
import requests
from fastapi.responses import StreamingResponse
from prometheus_client import Gauge, Histogram
from pydantic import BaseModel

from ..proto.docarray import LLMParams
from ..telemetry.opea_telemetry import opea_telemetry, tracer
from .constants import ServiceType
from .dag import DAG
from .logger import CustomLogger

logger = CustomLogger("comps-core-orchestrator")
LOGFLAG = os.getenv("LOGFLAG", False)
ENABLE_OPEA_TELEMETRY = os.getenv("ENABLE_OPEA_TELEMETRY", "false").lower() == "true"


class OrchestratorMetrics:
    """Class for managing metrics related to the orchestrator."""

    _instance_id = 0  # Static counter for unique metric prefixes

    def __init__(self) -> None:
        OrchestratorMetrics._instance_id += 1
        self._prefix = f"megaservice{self._instance_id}" if OrchestratorMetrics._instance_id > 1 else "megaservice"

        self.request_pending = Gauge(f"{self._prefix}_request_pending", "Count of currently pending requests")

        # Locking for thread safety in metric creation
        self._lock = threading.Lock()

        # Lazy initialization of token processing metrics
        self.first_token_latency = None
        self.inter_token_latency = None
        self.request_latency = None

        # Assign placeholder methods that will be replaced dynamically
        self.token_update = self._token_update_create
        self.request_update = self._request_update_create

    def _token_update_create(self, token_start: float, is_first: bool) -> float:
        """Initialize token latency metrics if not already created."""
        with self._lock:
            if self.token_update == self._token_update_create:  # Ensure only one thread initializes
                self.first_token_latency = Histogram(f"{self._prefix}_first_token_latency", "First token latency")
                self.inter_token_latency = Histogram(f"{self._prefix}_inter_token_latency", "Inter-token latency")
                self.token_update = self._token_update_real
        return self.token_update(token_start, is_first)

    def _request_update_create(self, req_start: float) -> None:
        """Initialize request latency metrics if not already created."""
        with self._lock:
            if self.request_update == self._request_update_create:
                self.request_latency = Histogram(f"{self._prefix}_request_latency", "LLM request/reply latency")
                self.request_update = self._request_update_real
        self.request_update(req_start)

    def _token_update_real(self, token_start: float, is_first: bool) -> float:
        """Record latency for token generation."""
        now = time.time()
        if is_first:
            self.first_token_latency.observe(now - token_start)
        else:
            self.inter_token_latency.observe(now - token_start)
        return now

    def _request_update_real(self, req_start: float) -> None:
        """Record total request latency."""
        self.request_latency.observe(time.time() - req_start)

    def pending_update(self, increase: bool) -> None:
        """Increment or decrement pending request count."""
        self.request_pending.inc() if increase else self.request_pending.dec()


class ServiceOrchestrator(DAG):
    """Manages multiple microservices in a DAG structure through Python API."""

    def __init__(self) -> None:
        self.metrics = OrchestratorMetrics()
        self.services = {}  # Service dictionary: id -> service
        super().__init__()

    def add(self, service):
        """Add a service to the orchestrator."""
        if service.name not in self.services:
            self.services[service.name] = service
            self.add_node_if_not_exists(service.name)
        else:
            raise ValueError(f"Service {service.name} already exists!")
        return self

    def flow_to(self, from_service, to_service):
        """Create a directed edge between two services in the DAG."""
        try:
            self.add_edge(from_service.name, to_service.name)
            return True
        except Exception as e:
            logger.error(f"Failed to create flow: {e}")
            return False

    @opea_telemetry
    async def schedule(self, initial_inputs: Dict | BaseModel, llm_parameters: LLMParams = LLMParams(), **kwargs):
        """Schedule the execution of the DAG using async tasks."""
        req_start = time.time()
        self.metrics.pending_update(True)

        result_dict = {}
        runtime_graph = DAG()
        runtime_graph.graph = copy.deepcopy(self.graph)

        if LOGFLAG:
            logger.info(f"Scheduling with inputs: {initial_inputs}")

        timeout = aiohttp.ClientTimeout(total=1000)
        async with aiohttp.ClientSession(trust_env=True, timeout=timeout) as session:
            pending_tasks = {
                asyncio.create_task(
                    self.execute(session, req_start, node, initial_inputs, runtime_graph, llm_parameters, **kwargs)
                )
                for node in self.ind_nodes()
            }

            while pending_tasks:
                done, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    response, node = await task
                    result_dict[node] = response

                    for d_node in runtime_graph.downstream(node):
                        if all(pred in result_dict for pred in runtime_graph.predecessors(d_node)):
                            inputs = self.process_outputs(runtime_graph.predecessors(d_node), result_dict)
                            pending_tasks.add(
                                asyncio.create_task(
                                    self.execute(session, req_start, d_node, inputs, runtime_graph, llm_parameters, **kwargs)
                                )
                            )

        self.metrics.pending_update(False)
        return result_dict, runtime_graph

    def process_outputs(self, prev_nodes: List, result_dict: Dict) -> Dict:
        """Combine outputs from multiple predecessor nodes."""
        combined_outputs = {}
        for node in prev_nodes:
            combined_outputs.update(result_dict[node])
        return combined_outputs

    def extract_chunk_str(self, chunk_str):
        """Extract and clean up a chunked response string."""
        if chunk_str == "data: [DONE]\n\n":
            return ""
        chunk_str = chunk_str.removeprefix("data: b'").removeprefix('data: b"')
        chunk_str = chunk_str.removesuffix("'\n\n").removesuffix('"\n\n')
        return chunk_str

    def token_generator(self, sentence: str, token_start: float, is_first: bool, is_last: bool) -> str:
        """Generate and yield tokens for streaming responses."""
        prefix = "data: "
        suffix = "\n\n"
        tokens = re.findall(r"\s?\S+\s?", sentence, re.UNICODE)
        for token in tokens:
            token_start = self.metrics.token_update(token_start, is_first)
            yield prefix + repr(token.replace("\\n", "\n").encode("utf-8")) + suffix
        if is_last:
            yield "data: [DONE]\n\n"
