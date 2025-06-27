from graph_db import get_driver, get_session
from graph.graph_flow_upsert import process_flow_response
from helpers.graph_flow_processor import process_execution_flow
from templates.prompt_templates import get_flow_extraction_prompt
from sampling import sample_helper
from analysis import get_file_content_full_path
import re
import json

async def extract_document_flow(mcp, repository: str, filename: str, classification, ctx) -> str:
    source_code = get_file_content_full_path(filename)

    if source_code.startswith("ERROR:"):
        await ctx.error(source_code)
        return source_code

    try:
        await ctx.info(f"Extracting flow for {filename} in repository {repository}")

        system_prompt, messages_for_llm = get_flow_extraction_prompt(
            filename=filename, classification=classification, source_code=source_code)

        response = await sample_helper(ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0)

        if not response:
            await ctx.error("Empty response from LLM")
            return "Error: Empty response from LLM"

        parsed = safe_extract_json(response)
        if not parsed:
            await ctx.warning(f"Could not extract valid JSON from LLM response.")
            return "Error: Invalid JSON from LLM"

        resource_uri_flow = f"program-flow://{repository}/{filename}"
        resource_content = json.dumps(parsed, indent=2) if isinstance(parsed, (dict, list)) else str(parsed)

        if isinstance(parsed, dict) and "flow" in parsed:
            driver = get_driver()
            with get_session(driver) as session:
                structured_flow = process_execution_flow(filename, parsed)
                process_flow_response(
                    session=session,
                    repository_name=repository,
                    filename=filename,
                    language="COBOL",
                    classification=classification,
                    flow_data=structured_flow
                )
            driver.close()
            await ctx.info(f"Program flow graph stored in Neo4j for {filename}")
            await ctx.info(f"Integration details included for impact analysis.")

        return resource_content

    except Exception as e:
        await ctx.error(f"Error during flow extraction: {e}")
        return f"Error during flow extraction: {e}"


# ----------------- Helper -----------------

def safe_extract_json(response_text):
    """
    Εξάγει JSON από text, αν υπάρχει, αλλιώς επιστρέφει None.
    """
    try:
        json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        json_content = json_match.group(1) if json_match else response_text
        return json.loads(json_content)
    except Exception:
        return None
