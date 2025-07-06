# Basic Project structure

```bash
legacy_analysis_server/
│
├── graph_db.py               # Driver και session management (μένει όπως είναι)
│
├── tools/                    # Ορατή επιφάνεια (MCP Tools), abstractions
│   ├── fetch_repository.py
│   ├── classify_repository.py
│   ├── extract_document_flow.py
│   └── analyze_file_edges.py (νέο - για edge ανάλυση ξεχωριστά)
│
├── helpers/
│   ├── graph_flow_processor.py   # Μένει εδώ για raw graph λογική
│   ├── llm_response_utils.py     # Νέο: General καθαρισμός / parsing LLM JSONs
│
├── graph/
│   ├── graph_upsert.py           # Upsert για βασικά στοιχεία (Repository, Document)
│   ├── graph_flow_upsert.py      # Upsert για execution flows (Παραμένει)
│   ├── graph_upsert_archimate.py # Νέο: Χαρτογράφηση σε Archimate terms
│   ├── graph_query.py            # Queries για αναζητήσεις / αναλύσεις
│
├── templates/
│   ├── prompt_templates.py       # Prompt selector ανά classification
│   ├── classify_file_template.py
│   ├── analyze_cobol_map.py
│   ├── extract_cobol_template.py
│   ├── extract_python_template.py
│   └── extract_generic_template.py  # Νέο για multi-lang επεκτασιμότητα
```