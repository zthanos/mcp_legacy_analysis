from pathlib import Path
import re


def extract_edges_prompt(content: str) -> tuple[str, str]:
    system_prompt = "You are an expert COBOL programmer and a seasoned static analysis tool."

    llm_message = f"""
You will analyze the following source code and identify all points of interaction with external or internal components. This includes:

- File operations such as `READ`, `WRITE`, `OPEN`, `CLOSE`, `SELECT`, `ASSIGN`
- Database access via `EXEC SQL`, embedded SQL statements
- Calls to other programs or modules using `CALL`
- Service or transaction instructions like `EXEC TRU`, `EXEC CICS`, `SEND`, `RECEIVE`

For each interaction, return a JSON object containing:
- `edge_type`: one of `file`, `database`, `service`, `program`
- `operation`: the action performed (e.g., `READ`, `CALL`, `EXEC SQL`, etc.)
- `target`: the file name, service name, database, or called module
- `line`: line number in the source code where the interaction occurs (if known)
- `details`: any extra relevant information (optional)

Return only a JSON array with all identified edges.

---

Source Code:
{content}


"""
    return system_prompt, llm_message

