## Running Ollama Third-Party Service

### Choosing a Model

You can get the model_id that ollama will launch from the [Ollama Library].

https://ollama.com/library/llama3.2

eg. LLM_MODEL_ID="llama3.2:1b"

### Getting the Host IP

#### Linux

Get your IP address
```sh
sudo apt install net-tools
ifconfig
```

Or you can try this way `$(hostname -I | awk '{print $1}')`

HOST_IP=$(hostname -I | awk '{print $1}') NO_PROXY=localhost LLM_ENDPOINT_PORT=9000 LLM_MODEL_ID="llama3.2:1b" docker compose up


### Ollama API

Once the Ollama server is running we can make API calls to the ollama API

https://github.com/ollama/ollama/blob/main/docs/api.md


## Download (Pull) a model

curl http://localhost:9000/api/pull -d '{
  "model": "llama3.2:1b"
}'

## Generate a Request

curl http://localhost:9000/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "Tell me a joke"
}'

# Technical Uncertainty
Q: Can we run multiple models simultaneously in the same Ollama server?

A: Yes, Ollama can handle multiple models, but you may need to specify the model explicitly when making API requests. Performance will depend on available resources.

Q: Is GPU acceleration required for running Ollama efficiently?

A: Not necessarily. While a GPU can significantly speed up inference, Ollama can run on a CPU as well. However, for larger models, a GPU is highly recommended.

Q: How can we persist models across container restarts?

A: You need to mount a persistent volume in Docker to store model files outside the container. This ensures they are not lost when the container stops.

Q: Does Ollama support fine-tuning models within the container?

A: Ollama does not natively support fine-tuning. You would need an external fine-tuning process and then load the trained model into Ollama.

Q: What API format does Ollama use for text generation requests?

A: Ollama provides an OpenAI-compatible API, meaning you can send requests in a format similar to OpenAI’s /v1/completions endpoint.

Q: In bridge mode, can we only access the Ollama API from another model within the Docker Compose setup?

A: No, the host machine can also access it.

Q: What does the port mapping 8008 -> 141414 mean?

A: The host machine will access the service through port 8008, while 141414 is the internal port of the service inside the container.

Q: If we pass LLM_MODEL_ID to the Ollama server on startup, will it automatically download the model?

A: No, it doesn't seem to work that way. The Ollama CLI might be managing multiple APIs, so you'll need to call the /pull API before generating text.

Q: If the model is downloaded inside the container, will it be deleted when the container stops?

A: Yes, the model is stored inside the container and will be lost when the container stops. To persist it, you need to mount a local volume. Additional setup may be required.

Q: The LLM service mentions that it supports text generation and suggests it works with TGI/vLLM. Do these frameworks have a standardized API, or does the system detect which one is running? Do we have to use a Xeon or Gaudi processor?

A: vLLM, TGI (Text Generation Inference), and Ollama provide OpenAI-compatible APIs, making them interchangeable in theory. As for hardware, while Xeon or Gaudi processors may offer optimizations, they are not strictly required.