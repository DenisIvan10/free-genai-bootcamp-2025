import ollama
import sys

client = ollama.Client()

conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Tell me a joke."},
]

# Stream the response
print("Streaming response: ", end="", flush=True)
for chunk in client.chat(
    model="llama3.2",
    messages=conversation,
    stream=True
):
    # Print without newline and flush immediately
    content = chunk.get('message', {}).get('content', '')
    print(content, end='', flush=True)

# Print final newline
print()