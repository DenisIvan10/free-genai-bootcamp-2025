from fastapi import HTTPException # type: ignore
from comps.cores.proto.api_protocol import ( # type: ignore
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatMessage,
    UsageInfo
)
from comps.cores.mega.constants import ServiceType, ServiceRoleType # type: ignore
from comps import MicroService, ServiceOrchestrator # type: ignore
import os

# Fetch environment variables with updated default values for clarity
EMBEDDING_SERVICE_HOST = os.getenv("EMBEDDING_SERVICE_HOST", "127.0.0.1")
EMBEDDING_SERVICE_PORT = int(os.getenv("EMBEDDING_SERVICE_PORT", "6000"))
LLM_SERVICE_HOST = os.getenv("LLM_SERVICE_HOST", "127.0.0.1")
LLM_SERVICE_PORT = int(os.getenv("LLM_SERVICE_PORT", "9000"))


class ExampleService:
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        print("Initializing ExampleService...")
        os.environ["TELEMETRY_ENDPOINT"] = ""
        self.host = host
        self.port = port
        self.endpoint = "/v1/example-service"
        self.service_orchestrator = ServiceOrchestrator()

    def configure_services(self):
        """Sets up remote services and integrates them into the orchestrator."""
        llm_service = MicroService(
            name="llm_service",
            host=LLM_SERVICE_HOST,
            port=LLM_SERVICE_PORT,
            endpoint="/v1/chat/completions",
            use_remote_service=True,
            service_type=ServiceType.LLM,
        )
        self.service_orchestrator.add(llm_service)

    def launch(self):
        """Initializes and starts the main service."""
        self.service = MicroService(
            self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint=self.endpoint,
            input_datatype=ChatCompletionRequest,
            output_datatype=ChatCompletionResponse,
        )
        self.service.add_route(self.endpoint, self.process_request, methods=["POST"])
        self.service.start()

    async def process_request(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        try:
            ollama_payload = {
                "model": request.model or "llama3.2:1b",
                "messages": [{"role": "user", "content": request.messages}],
                "stream": False
            }
            
            response_data = await self.service_orchestrator.schedule(ollama_payload)
            
            response_content = "No response received"
            if isinstance(response_data, tuple) and response_data:
                llm_result = response_data[0].get("llm_service/MicroService")
                if hasattr(llm_result, "body"):
                    response_content = "".join([chunk.decode("utf-8") async for chunk in llm_result.body_iterator])
            
            return ChatCompletionResponse(
                model=request.model or "default-model",
                choices=[
                    ChatCompletionResponseChoice(
                        index=0,
                        message=ChatMessage(role="assistant", content=response_content),
                        finish_reason="stop"
                    )
                ],
                usage=UsageInfo(prompt_tokens=0, completion_tokens=0, total_tokens=0)
            )
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {error}")


if __name__ == "__main__":
    service_instance = ExampleService()
    service_instance.configure_services()
    service_instance.launch()
