from graph_db import get_driver, get_session, insert_flow_graph
from templates.prompt_templates import get_flow_extraction_prompt
from sampling import sample_helper
from analysis import get_file_content_full_path
import re
import json

async def get_file_flow(mcp, repository: str, filename: str, classification, ctx) -> str:
    source_code = get_file_content_full_path(filename)
    
    if source_code.startswith("ERROR:"):
        await ctx.error(source_code)
        return source_code
    
    try:
        await ctx.info(f"Extracting flow for {filename} in repository {repository}")
        
        system_prompt, messages_for_llm = get_flow_extraction_prompt(
            filename=filename, classification=classification, source_code=source_code)
        
        response = await sample_helper(
            ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0)

        if not response:
            await ctx.error("Empty response from LLM")
            return "Error: Empty response from LLM"
        
        json_match = re.search(r'(\{.*\})', response, re.DOTALL)
        json_content = json_match.group(1) if json_match else response

        try:
            parsed = json.loads(json_content)
        except Exception as e:
            await ctx.warning(f"Response is not valid JSON: {e}")
            parsed = {"error": "Invalid JSON", "raw_response": response}

        resource_uri_flow = f"program-flow://{repository}/{filename}"
        resource_content = json.dumps(parsed, indent=2) if isinstance(parsed, (dict, list)) else str(parsed)

        # Neo4j Aura Εισαγωγή Flow Graph
        if isinstance(parsed, dict) and "flow_graph" in parsed:
            driver = get_driver()
            with get_session(driver) as session:
                insert_flow_graph(session, parsed)
            driver.close()
            await ctx.info(f"Program flow graph stored in Neo4j for {filename}")
            await ctx.info(f"Integration details included in graph for impact analysis.")


        return resource_content
        
    except Exception as e:
        await ctx.error(f"Error during flow extraction: {e}")
        return f"Error during flow extraction: {e}"






# from analysis import get_file_content_full_path
# from fastmcp.resources import  TextResource, resource_manager
# from templates.prompt_templates import get_flow_extraction_prompt
# from sampling import sample_helper
# import re
# import json


# async def get_file_flow(mcp, repository: str, filename: str, classification, ctx) -> str:
#     source_code = get_file_content_full_path(filename)
#     if source_code.startswith("ERROR:"):
#         await ctx.error(source_code)
#         return source_code
#     try:
#         await ctx.info(f"Extracting flow for {filename} in repository {repository}")
#         system_prompt, messages_for_llm = get_flow_extraction_prompt(filename=filename, classification=classification, source_code=source_code)
#         print(f"System prompt: {system_prompt}")
#         print(f"Messages for LLM: {messages_for_llm}")
#         await ctx.info(f"System prompt: {system_prompt}")
#         await ctx.info(f"Messages for LLM: {messages_for_llm[:200]}")
#         response = await sample_helper(ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0)

#         if not response:
#             await ctx.error("Empty response from LLM")
#             return "Error: Empty response from LLM"
        
#         # Try to extract JSON from response if it contains extra text
#         json_match = re.search(r'(\{.*\})', response, re.DOTALL)
#         if json_match:
#             json_content = json_match.group(1)
#         else:
#             json_content = response
            
#         # Validate JSON
#         try:
#             parsed = json.loads(json_content)
#         except Exception as e:
#             await ctx.warning(f"Response is not valid JSON: {e}")
#             parsed = {"error": "Invalid JSON", "raw_response": response}

#         # Register result as resource - FastMCP format
#         resource_uri_flow = f"program-flow://{repository}/{filename}"
#         resource_content = json.dumps(parsed, indent=2) if isinstance(parsed, (dict, list)) else str(parsed)
        
#         # Save as resource
#         # resource = TextResource(
#         #     uri=resource_uri_flow,
#         #     name=f"Program Flow for {repository}",
#         #     description=f"Program execution flow extracted from {repository}",
#         #     tags=[classification, "program-flow"],
#         #     text=resource_content
#         # )
#         # mcp.add_resource(resource)
        
#         return resource_content
        
#     except Exception as e:
#         await ctx.error(f"Error calling LLM for flow extraction: {e}")
#         return f"Error calling LLM for flow extraction: {e}"


