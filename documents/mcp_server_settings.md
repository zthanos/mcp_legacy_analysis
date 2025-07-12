# MCP Server Settings

This document explains how to configure MCP (Mainframe Code Processing) servers for your local or remote environment. The configuration is provided in JSON format and can be used to define how different MCP server instances are started and accessed.

## How to Set Up MCP Server Configuration

1. **Purpose:**
   - This configuration allows you to define multiple MCP server instances, each with its own connection method (either via HTTP URL or by specifying a command to launch the server).
   - You can also specify which servers are allowed for certain operations, such as chat sampling.

2. **Usage:**
   - Copy the JSON example below into your configuration file (e.g., `mcp_server_settings.json`).
   - Adjust the server URLs, commands, and arguments as needed for your environment.
   - Use this configuration in your application or tooling to connect to and manage MCP servers.

---

```json
{
  "mcpServers": {
    // Example 1: Connect to a running server via HTTP
    "legacy-analyzer-sse-v1-01": {
      "url": "http://localhost:9000/sse" // The URL where the MCP server is accessible
    },
    // Example 2: Start a server using a command
    "legacy-analyzer-v1-02": {
      "command": "uv", // The command to run (e.g., uv, python, etc.)
      "args": [
        "run", // Arguments to the command
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
        "python", // The Python interpreter
        "G:\\source\\python\\mcp_legacy_analysis\\main.py" // Path to the main server script
      ]
    }
  },
  // Specify which servers are allowed for chat sampling or other features
  "chat.mcp.serverSampling": {
    "Global in Code: legacy-analyzer-sse-v1-01": {
      "allowedDuringChat": true // Allow this server to be used during chat
    }
  }
}
```

---

## Key Sections Explained

- **mcpServers**: A dictionary of server configurations. Each key is a unique server name.
  - **url**: Directly connect to a running MCP server at the specified HTTP address.
  - **command** and **args**: Define how to start a server process locally, including dependencies and the main script.
- **chat.mcp.serverSampling**: Controls which servers are available for specific features (e.g., chat sampling). Set `allowedDuringChat` to `true` to enable.

---

## What is 'uv' and what are the arguments for?

- **uv**: A fast Python package and environment manager, used here to run Python applications with specific dependencies in an isolated environment.
- **run**: Tells `uv` to execute the following script or command.
- **--with <package>**: Installs or ensures the specified package (and version) is available in the environment before running the script. This allows you to specify all required dependencies inline.
- **python**: The Python interpreter to use for running the main script.
- **main.py**: The entry point script for the MCP server.

This setup ensures all dependencies are available and up-to-date each time the server is started, making the environment reproducible and easy to manage.

---

**Tip:**
- Adjust the paths and versions to match your local setup.
- You can add more servers by duplicating and editing the entries in the `mcpServers` section.
- For more advanced setups, refer to your project's documentation or contact your system administrator.

