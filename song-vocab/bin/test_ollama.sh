#!/bin/bash

echo "Testing Ollama API..."
curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2",
    "messages": [
      {
        "role": "user",
        "content": "Tell me a joke"
      }
    ]
  }' | jq .

echo "Done!"
