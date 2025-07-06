```bash
 uvicorn mcp_instance:mcp --reload  
```


## Run MCP Inspector
```bash
npx @modelcontextprotocol/inspector uvicorn main:app --reload

```

## Run model on llama shell
```bash
ollama run deepseek-coder-v2
```

```json
{
  "mcpServers": {
    "ollama-wrapper": {
      "command": "uvicorn",
      "args": ["mcp_instance:app", "--reload"],
      "note": "FastAPI MCP wrapper to Ollama"
    }
  }
}


```

```bash
npx @modelcontextprotocol/inspector --config mcp.json --server ollama-wrapper
```