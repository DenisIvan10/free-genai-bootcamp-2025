import json
from fastapi import HTTPException
from comps.cores.proto.api_protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatMessage,
    UsageInfo
)
from comps.cores.mega.constants import ServiceType, ServiceRoleType
from comps import MicroService, ServiceOrchestrator
import os
import aiohttp
from comps.cores.mega.utils import handle_message
from comps.cores.proto.docarray import LLMParams
from fastapi import Request
from fastapi.responses import StreamingResponse

EMBEDDING_SERVICE_HOST_IP = os.getenv("EMBEDDING_SERVICE_HOST_IP", "0.0.0.0")
EMBEDDING_SERVICE_PORT = os.getenv("EMBEDDING_SERVICE_PORT", 6000)
LLM_SERVICE_HOST_IP = os.getenv("LLM_SERVICE_HOST_IP", "0.0.0.0")
LLM_SERVICE_PORT = os.getenv("LLM_SERVICE_PORT", 9000)


class ExampleService:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.endpoint = "/v1/example-service"
        self.megaservice = ServiceOrchestrator()
        os.environ["LOGFLAG"] = "true"  # Enable logging for debugging

    async def check_ollama_connection(self):
        """Verify connection to the Ollama service."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://{LLM_SERVICE_HOST_IP}:{LLM_SERVICE_PORT}/api/tags"
                print(f"\nChecking Ollama connection: {url}")
                async with session.get(url) as response:
                    print(f"Ollama connection status: {response.status}")
                    return response.status == 200
        except Exception as e:
            print(f"Failed to connect to Ollama: {e}")
            return False

    def add_remote_service(self):
        """Configure and add the remote LLM service."""
        llm = MicroService(
            name="llm",
            host=LLM_SERVICE_HOST_IP,
            port=LLM_SERVICE_PORT,
            endpoint="/v1/chat/completions",
            use_remote_service=True,
            service_type=ServiceType.LLM,
        )
        print("\nConfiguring LLM service:")
        print(f"- Host: {LLM_SERVICE_HOST_IP}")
        print(f"- Port: {LLM_SERVICE_PORT}")
        print(f"- Endpoint: {llm.endpoint}")
        print(f"- Full URL: http://{LLM_SERVICE_HOST_IP}:{LLM_SERVICE_PORT}{llm.endpoint}")
        self.megaservice.add(llm)

    def start(self):
        """Start the ExampleService as a microservice."""
        self.service = MicroService(
            self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint=self.endpoint,
            input_datatype=ChatCompletionRequest,
            output_datatype=ChatCompletionResponse,
        )
        self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])
        print(f"Service initialized at endpoint: {self.endpoint}")
        self.service.start()

    async def handle_request(self, request: Request):
        """Handle incoming chat completion requests."""
        data = await request.json()
        print("\nReceived request data:\n", data)
        stream_opt = data.get("stream", True)
        chat_request = ChatCompletionRequest.model_validate(data)
        
        parameters = LLMParams(
            max_tokens=chat_request.max_tokens or 1024,
            top_k=chat_request.top_k or 10,
            top_p=chat_request.top_p or 0.95,
            temperature=chat_request.temperature or 0.01,
            frequency_penalty=chat_request.frequency_penalty or 0.0,
            presence_penalty=chat_request.presence_penalty or 0.0,
            repetition_penalty=chat_request.repetition_penalty or 1.03,
            stream=stream_opt,
            model=chat_request.model,
            chat_template=chat_request.chat_template or None,
        )
        initial_inputs = {"messages": chat_request.messages}

        print("\nGenerated LLM Parameters:\n", parameters)
        result_dict, runtime_graph = await self.megaservice.schedule(
            initial_inputs=initial_inputs,
            llm_parameters=parameters
        )
        print("\nProcessing response from LLM service...")

        for node, response in result_dict.items():
            if isinstance(response, StreamingResponse):
                print("\nStreaming response detected")
                return response

        print("\nNo streaming response detected")
        last_node = runtime_graph.all_leaves()[-1]
        if last_node in result_dict:
            service_result = result_dict[last_node]
            if isinstance(service_result, dict):
                if 'choices' in service_result and service_result['choices']:
                    response = service_result['choices'][0].get('message', {}).get('content', '')
                elif 'error' in service_result:
                    error_msg = service_result['error'].get('message', 'Unknown error')
                    raise HTTPException(status_code=400, detail=error_msg)
                else:
                    raise HTTPException(status_code=500, detail="Unexpected response format from LLM service")
            else:
                response = service_result
        else:
            raise HTTPException(status_code=500, detail="No response received from LLM service")

        print("\nReturning non-streaming response:\n", response)
        return ChatCompletionResponse(
            model="chatqna",
            choices=[ChatCompletionResponseChoice(
                index=0,
                message=ChatMessage(role="assistant", content=response),
                finish_reason="stop"
            )],
            usage=UsageInfo()
        )

example = ExampleService()
example.add_remote_service()
example.start()
