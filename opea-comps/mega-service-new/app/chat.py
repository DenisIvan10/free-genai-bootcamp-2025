from comps import ServiceOrchestrator, ServiceRoleType, MicroService
from comps.cores.proto.api_protocol import (
    ChatCompletionRequest, 
    ChatCompletionResponse
)
from fastapi import Request

class Chat:
    def __init__(self):
        print('Initializing Chat service...')
        self.megaservice = ServiceOrchestrator()
        self.endpoint = '/endpoint'
        self.host = '0.0.0.0'
        self.port = 8888

    def add_remote_services(self):
        print('Adding remote services...')

    def start(self):
        print(f'Starting Chat service on {self.host}:{self.port}{self.endpoint}...')
        self.service = MicroService(
            name=self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint=self.endpoint,
            input_datatype=ChatCompletionRequest,
            output_datatype=ChatCompletionResponse,
        )

        self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])
        self.service.start()

    def handle_request(self, request: Request):
        print('Handling request...')

if __name__ == '__main__':
    print('Launching Chat service...')
    chat = Chat()
    chat.add_remote_services()
    chat.start()
