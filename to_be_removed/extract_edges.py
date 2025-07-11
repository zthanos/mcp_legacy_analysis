from graph_db import get_file_full_path
from analysis import get_file_content_full_path

from sampling import sample_helper

async def execute_extract_edges(session, repository_name, filename: str, ctx) -> str:
    try:
        full_path = get_file_full_path(session, repository_name=repository_name, filename=filename)
        print(f"full_path: {full_path}")
        if full_path:
            content = get_file_content_full_path(full_path)
            await ctx.info(f"Extracting edges from {filename}...")
            system_prompt, messages_for_llm = extract_edges_prompt(content)
            response = await sample_helper(ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0)
            return response
        else:
            await ctx.error(f"File not found: {filename}")
            return f"Error: File not found: {filename}"
    except Exception as e:
        print(f"Error finding edges: {e}")
        await ctx.error(f"Error finding edges: {e}")
        return f"Error: {e}"    



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

