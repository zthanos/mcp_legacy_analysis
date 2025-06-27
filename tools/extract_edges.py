from graph_db import get_file_full_path
from analysis import get_file_content_full_path
from templates.extract_edges import extract_edges_prompt
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
