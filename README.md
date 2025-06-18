# MCP Legacy Analysis

This project provides a server and tools for static analysis of legacy codebases, especially mainframe technologies such as COBOL, CLIST, and Python. It leverages LLMs to extract program flow, data structures, and perform file classification, making it easier to understand and modernize legacy systems.

## Features

- **Repository Fetching:** Clone and register COBOL/mainframe repositories for analysis.
- **File Classification:** Automatically detect programming language or file type using LLMs.
- **Data Structure Extraction:** Extract COBOL data structures and convert them to human-readable pseudocode.
- **Program Flow Analysis:** Generate JSON-based control flow graphs for COBOL, CLIST, and Python code.
- **Resource Management:** Register and manage analysis results as resources for further processing.
- **C4 Model Generation:** Generate C4 architecture diagrams from analyzed system components.
- **FastMCP Integration:** Built on [FastMCP](https://github.com/modelcontextprotocol/fastmcp) for scalable, modular tool orchestration.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Node.js (for MCP Inspector, optional)
- Git (for repository cloning)

## Installation

### 1. Install `uv` Package Manager

`uv` is a fast Python package manager and virtual environment tool.

```bash
# On Windows (PowerShell)
iwr https://astral.sh/uv/install.ps1 -useb | iex

# On macOS/Linux
curl -Ls https://astral.sh/uv/install.sh | sh
```

See [uv installation docs](https://github.com/astral-sh/uv#installation) for more options.

### 2. Set Up the Project

```bash
# Sync dependencies and create virtual environment
uv sync

# Run the main server
uv run main.py
```

## Usage

### Run MCP Server Inspector

```bash
npx @modelcontextprotocol/inspector uv run python main.py
```

### MCP Server Configuration in VS Code

Add the following to your VS Code settings for MCP integration:

```json
"servers": {
    "legacy-code-analyzer-server-v1-01": {
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
            "python",
            "G:\\source\\python\\mcp_legacy_analysis\\main.py"
        ]
    }
},
"chat.mcp.serverSampling": {
    "Global in Code: legacy-code-analyzer-server-v1-01": {
        "allowedDuringChat": true
    }
}
```

## Project Structure

- `main.py` — Entry point for the FastMCP server.
- `legacy_analysis_server.py` — Registers tools and resources for analysis.
- `analysis.py` — File content retrieval and classification logic.
- `data_structure.py` — COBOL data structure extraction and pseudocode conversion.
- `flow_analysis.py` — Program flow extraction for COBOL, CLIST, and Python.
- `sampling.py` — LLM sampling helper.
- `templates/` — Prompt templates for various analysis tasks.
- `workspace/` — Cloned repositories and analysis artifacts.

## License

MIT License. See [LICENSE](LICENSE) for details.