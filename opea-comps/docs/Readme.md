# Microservices
A MicroService instance serves two primary functions:
1. It acts as an API Gateway to an underlying service, such as an LLM, Embedding, or Reranker.
2. It integrates with the Orchestrator, enabling seamless execution of workflows within a directed acyclic graph (DAG).

# FastAPI-based Architecture

Each MicroService extends HTTPService, which itself builds upon BaseService.
- BaseService provides core abstract methods.
- HTTPService initializes a FastAPI application, served via Uvicorn.
- MicroService adds specific functionalities tailored to different AI services.

Predefined endpoints in HTTPService include:
- /v1/health_check – Health status verification.
- /v1/health – Alias for /v1/health_check.
- /v1/statistics – Provides runtime metrics.

# Defining a MicroService
Below is an example of configuring an LLM as a MicroService:

```py
llm = MicroService(
    name="llm",
    host=LLM_SERVER_HOST_IP,
    port=LLM_SERVER_PORT,
    endpoint="/v1/chat/completions",
    use_remote_service=True,
    service_type=ServiceType.LLM,
    service_role=ServiceRoleType.MICROSERVICE,
)
```

# MegaService: A Higher-Level MicroService
A MegaService is essentially a MicroService but with ServiceRoleType.MEGASERVICE. It provides a structured way to expose endpoints that interact with multiple MicroServices.

```py
self.service = MicroService(
    name=self.__class__.__name__,
    service_role=ServiceRoleType.MEGASERVICE,
    host=self.host,
    port=self.port,
    endpoint="/v1/example-service",
    input_datatype=ChatCompletionRequest,
    output_datatype=ChatCompletionResponse,
)
self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])
self.service.start()
```

## ServiceOrchestrator
The [ServiceOrchestrator](https://github.com/opea-project/GenAIComps/blob/main/comps/cores/mega/orchestrator.py) is the actual MegaService. 

```py
self.megaservice = ServiceOrchestrator()
```

ServiceOrchestrator allows you to define the workflow between your services and this flow is managed with a [directed acyclic graph (DAG)](https://en.wikipedia.org/wiki/Directed_acyclic_graph).

Here is an example of us creating a workflow with the ServiceOrchestrator from multiple MicroServices.
Notice we add the services to ServiceOrchestrator and then we define the flow.

```py
self.megaservice.add(guardrail_in).add(embedding).add(retriever).add(rerank).add(llm)
self.megaservice.flow_to(guardrail_in, embedding)
self.megaservice.flow_to(embedding, retriever)
self.megaservice.flow_to(retriever, rerank)
self.megaservice.flow_to(rerank, llm)
```

# Utility Modules
The framework provides several utility modules:
- comps.cores.mega.utils – Functions to check port availability and retrieve internal IPs.
- comps.cores.proto.api_protocol – Defines data structures for API requests and responses.
- comps.cores.proto.docarray – Handles data representation for multimodal AI tasks.

DocArray is leveraged for efficient storage, retrieval, and transmission of multimodal data.

Example usage:

```py
from comps.cores.mega.utils import handle_message
from comps.cores.proto.api_protocol import (
    ChatCompletionRequest, ChatCompletionResponse, ChatCompletionResponseChoice,
    ChatMessage, UsageInfo,
)
from comps.cores.proto.docarray import LLMParams, RerankerParms, RetrieverParms
```