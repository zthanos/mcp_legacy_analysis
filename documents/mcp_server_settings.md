# MCP Server Settings


```json
{
  "mcpServers": {
    "legacy-analyzer-sse-v1-01": {
      "url": "http://localhost:9000/sse"
    },
    "legacy-analyzer-v1-02": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp>=2.8.0",
        "--with",
        "gitpython>=3.1.44",
        "--with",
        "mcp-llm>=0.1.0",
        "--with",
        "uvicorn>=0.34.3",
        "--with",
        "aiohttp>=3.12.13",
        "--with",
        "neo4j>=5.28.1",
        "--with",
        "python-dotenv>=1.1.0",
        "python",
        "G:\\source\\python\\mcp_legacy_analysis\\main.py"
      ]
    }
  },
  "chat.mcp.serverSampling": {
    "Global in Code: legacy-analyzer-sse-v1-01": {
      "allowedDuringChat": true
    }
  }
} 
```