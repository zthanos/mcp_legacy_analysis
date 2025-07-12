# Project Structure Overview

This document describes the main components and files in the project, providing a high-level overview of their purpose.

```bash
mcp_legacy_analysis/
│
├── main.py                    # Main entry point for the application
├── legacy_analysis_server.py  # Server for handling legacy analysis requests
├── graph_db.py                # Neo4j driver and session management
├── mcp_client.py              # Client for interacting with MCP services
├── sampling.py                # Sampling utilities for analysis
├── languages_config.json      # Configuration for supported languages
├── pyproject.toml             # Python project dependencies and settings
├── README.md                  # Project documentation and usage
│
├── data/                      # Example and test data files
│   ├── dogemain.json
│   └── kicks.json
│
├── documents/                 # Documentation and architecture diagrams
│   ├── examples.md
│   ├── mcp_architecture.png
│   ├── mcp_architecture1.png
│   ├── mcp_sequence.png
│   ├── mcp_server_settings.md
│   ├── mcp-architecture.md
│   ├── project_structure.md
│   └── Usefull Commands.md
│
├── graph/                     # Graph database upsert and query logic
│   ├── __init__.py
│   ├── graph_upsert.py            # Upsert basic entities (Repository, Document)
│   ├── graph_flow_upsert.py       # Upsert execution flows
│   ├── graph_upsert_archimate.py  # Map entities to Archimate terms
│   └── graph_query.py             # Query and analyze graph data
│
├── helpers/                   # Utility modules for processing and responses
│   ├── __init__.py
│   ├── graph_flow_processor.py    # Raw graph logic and flow processing
│   └── response_helper.py         # Helpers for formatting and parsing responses
│
├── templates/                 # Prompt and template generators for LLMs
│   ├── __init__.py
│   ├── prompt_templates.py        # Selects prompt by classification
│   ├── classify_file_template.py
│   ├── analyze_cobol_map.py
│   ├── cobol_context_prompt.py
│   ├── code_analyzer_prompt_generator.py
│   ├── extract_clist_template.py
│   ├── extract_cobol_template.py
│   ├── extract_python_template.py
│   ├── extract_edges.py
│   └── extract_generic_template.py # For multi-language extensibility
│
├── tools/                     # MCP tool implementations and utilities
│   ├── __init__.py
│   ├── repository.py              # Repository related actions
│   ├── classify_repository.py     # Classifies repository contents
│   ├── extract_document_flow.py   # Extracts execution flow from documents
│   ├── extract_edges.py           # Extracts edges for graph analysis
│   └── document.py                # Document content and metadata utilities
│
├── utils/                     # General utility modules
│   └── logger.py                  # Logging utilities
│
├── tests/                     # Unit and integration tests
│   ├── __init__.py
│   ├── convert_complex_llm_steps_to_flow_test.py
│   ├── convert_llm_steps_to_flow_test.py
│   └── process_flow_response.py
│
├── prompts/                   # Prompt scripts for LLMs
│   └── code_analysis_prompt.py
│
├── mcp_debug.log              # Debug log output
├── uv.lock                    # Lock file for uv package manager
├── workspace/                 # Workspace for temporary or user files
```