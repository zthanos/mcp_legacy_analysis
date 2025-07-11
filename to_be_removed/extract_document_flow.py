from graph_db import get_driver, get_session
from helpers.graph_flow_processor import process_execution_flow
from graph.graph_upsert_archimate import (
    upsert_technology_system,
    upsert_technology_artifact,
    upsert_technology_function,
    upsert_internal_flow,
    upsert_external_interaction
)
from sampling import sample_helper
from tools.document import get_document_content_full_path


import re
import json

async def extract_language_specific_flow(mcp, language: str, source_code: str, repository_name: str, filename: str, ctx) -> str:
    system_prompt, messages_for_llm = flow_extraction(source_code=source_code, filename=filename, repository_name=repository_name, program_id=filename, language=language)
    response = await sample_helper(ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0)
    print(f"response: {response}")
    if not response:
        await ctx.error("Empty response from LLM")
        return "Error: Empty response from LLM"
    parsed = safe_extract_json(response)
    return response

async def extract_flow_with_specific_prompt(mcp, system_prompt: str, llm_prompt: str, ctx) -> str:
    response = await sample_helper(ctx=ctx, messages_for_llm=llm_prompt, system_prompt=system_prompt, temperature=0)
    print(f"system_prompt: {system_prompt}")
    print(f"messages_for_llm: {llm_prompt}")
    await ctx.debug(f"response: {response}")
    if not response:
        await ctx.error("Empty response from LLM")
        return "Error: Empty response from LLM"
    print(f"response: {response}")

    response = await sample_helper(ctx=ctx, messages_for_llm=response, system_prompt=system_prompt, temperature=0)
    await ctx.debug(f"response: {response}")
    match = re.search(r"```json\s*([\s\S]*?)\s*```", response)
    if match:
        json_str = match.group(1).strip()
        await ctx.debug(json_str)
        return json_str

    
    return response    


async def extract_document_flow(mcp, repository: str, filename: str, classification, ctx) -> str:
    source_code = get_document_content_full_path(filename)

    if source_code.startswith("ERROR:"):
        await ctx.error(source_code)
        return source_code

    try:
        await ctx.info(f"Extracting flow for {filename} in repository {repository}")

        system_prompt, messages_for_llm = get_flow_extraction_prompt(
            filename=filename, classification=classification, source_code=source_code
        )

        print(f"messages_for_llm: {messages_for_llm}")
        response = await sample_helper(ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0)
        print(f"response: {response}")
        if not response:
            await ctx.error("Empty response from LLM")
            return "Error: Empty response from LLM"

        parsed = safe_extract_json(response)
        if not parsed:
            await ctx.warning(f"Could not extract valid JSON from LLM response.")
            await ctx.debug(f"LLM response: {response}")
            return f"Error: Invalid JSON from LLM\n{response}"

        await ctx.info(f"Processing execution flow for {filename}...")
        processed_flow = process_execution_flow(filename, parsed)

        driver = get_driver()
        with get_session(driver) as session:
            
            # Step 1: Upsert System & Artifact
            upsert_technology_system(session, repository)
            upsert_technology_artifact(session, repository, filename, filename, "Unknown", classification)  # Optional: Detect language

            # Step 2: Upsert Functions & Flows
            for node in processed_flow["flow_graph"]:
                upsert_technology_function(session, filename, node["node"], node.get("is_entry_point", False))

                for edge in node.get("edges_to", []):
                    if edge["integration_type"] == "internal":
                        upsert_internal_flow(session, node["node"], edge["target"], filename, edge["transfer_type"])
                    else:
                        upsert_external_interaction(session, node["node"], edge["target"], filename, edge["transfer_type"])

        driver.close()

        await ctx.info(f"Flow graph stored in Neo4j with Archimate terms for {filename}.")
        return json.dumps(processed_flow, indent=2)

    except Exception as e:
        await ctx.error(f"Error during flow extraction: {e}")
        return f"Error during flow extraction: {e}"


# ----------------- Helper -----------------

def safe_extract_json(response_text):
    try:
        json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        json_content = json_match.group(1) if json_match else response_text
        return json.loads(json_content)
    except Exception:
        return None
