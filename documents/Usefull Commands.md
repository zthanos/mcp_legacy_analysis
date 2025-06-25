```bash
 uvicorn mcp_instance:mcp --reload  
```

```bash
npx @modelcontextprotocol/inspector uvicorn main:app --reload

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