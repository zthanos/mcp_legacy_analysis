from analysis import get_file_content
from fastmcp.resources import  TextResource
from templates.prompt_templates import get_flow_extraction_prompt
from sampling import sample_helper
import re
import json


async def extract_flow(mcp, repository: str, filename: str, classification, ctx) -> str:
    source_code = get_file_content(repository, filename)
    if source_code.startswith("ERROR:"):
        await ctx.error(source_code)
        return source_code
    try:
        system_prompt, messages_for_llm = get_flow_extraction_prompt(source_code)
        response = await sample_helper(ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0.7)

        if not response:
            await ctx.error("Empty response from LLM")
            return "Error: Empty response from LLM"
        
        # Try to extract JSON from response if it contains extra text
        json_match = re.search(r'(\{.*\})', response, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = response
            
        # Validate JSON
        try:
            parsed = json.loads(json_content)
            await ctx.info("Successfully parsed JSON response")
        except Exception as e:
            await ctx.warning(f"Response is not valid JSON: {e}")
            await ctx.info(f"Raw response: {response[:200]}...")
            parsed = {"error": "Invalid JSON", "raw_response": response}

        # Register result as resource - FastMCP format
        resource_uri_flow = f"program-flow://{repository}/{filename}"
        resource_content = json.dumps(parsed, indent=2) if isinstance(parsed, (dict, list)) else str(parsed)
        
        # Save as resource
        resource = TextResource(
            uri=resource_uri_flow,
            name=f"Program Flow for {repository}",
            description=f"Program execution flow extracted from {repository}",
            classification=classification,
            text=resource_content
        )
        
        mcp.add_resource(resource)
        await ctx.info(f"Program flow resource saved with URI: {resource_uri_flow}")
        
        return resource_content
        
    except Exception as e:
        await ctx.error(f"Error calling LLM for flow extraction: {e}")
        return f"Error calling LLM for flow extraction: {e}"

