# Running Ollama locally

```docker-compose
version: '3.8'

services:
  ollama:
    image: ollama/ollama:rocm # Use the ROCm-specific image tag
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    # Explicitly pass the AMD GPU devices into the container

    environment:
      # This environment variable is still useful for Ollama itself
      # to properly detect and utilize the ROCm devices passed.
      - ROCM_VISIBLE_DEVICES=all
    # Remove the 'deploy' section entirely, as it was causing issues
    # with NVIDIA hooks and is not needed with explicit 'devices' mapping.
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - capabilities: ["gpu"]

volumes:
  ollama_data:
```