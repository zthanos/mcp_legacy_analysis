# Running Ollama locally

This guide will help you set up and run the Ollama LLM (Large Language Model) locally using Docker Compose, and show you how to add and use specific models in your local instance.

## 1. Start Ollama LLM with Docker Compose

The following `docker-compose.yml` file defines a service for running Ollama with AMD GPU support (using the ROCm image). It also sets up persistent storage for your models and data.

```docker-compose
yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:rocm # Use the ROCm-specific image tag for AMD GPUs
    container_name: ollama
    ports:
      - "11434:11434" # Exposes Ollama's API on port 11434
    volumes:
      - ollama_data:/root/.ollama # Persists model data between restarts
    environment:
      - ROCM_VISIBLE_DEVICES=all # Ensures Ollama detects all available AMD GPUs
    # The 'deploy' section is omitted as it's not needed for local development

volumes:
  ollama_data:
```

**Instructions:**
1. Save the above content as `docker-compose.yml` in your project directory.
2. Open a terminal and navigate to the directory containing your `docker-compose.yml` file.
3. Start the Ollama service by running:
   ```bash
   docker-compose up -d
   ```
   This will download the Ollama image (if not already present), create the container, and start the service in the background.
4. Once running, Ollama will be accessible on your local machine at port 11434.

---

# Adding models to Ollama LLM

After starting the Ollama service, you can add and use specific language models. This is done by running commands inside the Ollama container or from your host if the `ollama` CLI is available.

## 2. Add and run a model using the Ollama shell


To add [(download)]('https://ollama.com/library') and run a model, use the following command:

```bash
ollama run deepseek-coder-v2
```

- This command will download the `deepseek-coder-v2` model (if not already present) and start an interactive shell for using the model.
- You can replace `deepseek-coder-v2` with the name of any other supported model.

**Instructions:**
1. Make sure the Ollama service is running (see previous section).
2. Open a new terminal window.
3. Run the above command. If you are inside the container, just type it directly. If you are on the host and have the `ollama` CLI installed, you can run it from your host as well.
4. Follow the prompts to interact with the model.

---

**Summary:**
- Use the provided Docker Compose file to run Ollama LLM locally with persistent storage and GPU support.
- Add and use models by running `ollama run <model-name>` in the shell.
- For more advanced usage, refer to the official Ollama documentation.