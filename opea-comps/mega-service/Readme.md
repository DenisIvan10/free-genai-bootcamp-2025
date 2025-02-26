# Running the LLM Service
We use Ollama, which is delivered via Docker Compose.

You can set the port that the LLM listens on. The ideal port is 9000, considering many existing OPEA megaservice default ports. If not set, it will default to 8008.

```sh
LLM_ENDPOINT_PORT=9000 docker compose up
```

When you start Ollama, the model is not downloaded by default. You need to download the model via the Ollama API.

# Downloading (Pulling) a Model

```sh
curl http://localhost:9000/api/pull -d '{
  "model": "llama3.2:1b"
}'
```

# Accessing the Jaeger UI

Running Docker Compose should automatically start Jaeger.

```sh
http://localhost:16686/
```

## Running the Mega Service Example

```sh
python app.py
```

# Testing the App
Install JQ to format JSON output:

```sh
sudo apt-get install jq
```
- For more details: JQ Download
https://jqlang.org/download/


# Navigate to the opea-comps/mega-service directory:

```sh
curl -X POST http://localhost:8000/v1/example-service \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:1b",
    "messages": "Hello, how are you?"
  }' | jq '.' > output/$(date +%s)-response.json
```

```sh
  curl -X POST http://localhost:8000/v1/example-service \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello, this is a test message"
      }
    ],
    "model": "llama3.2:1b",
    "max_tokens": 100,
    "temperature": 0.7
  }' | jq '.' > output/$(date +%s)-response.json
```