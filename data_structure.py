from analysis import get_file_content
from fastmcp.resources import  TextResource
import re
import json


class ExtractDataStructures:
    async def cobol_data_structure(mcp, repository: str, filename: str, ctx) -> str:
        cobol_code = get_file_content(repository, filename)
        if cobol_code.startswith("ERROR:"):
            await ctx.error(cobol_code)
            return cobol_code

        # extract with regex from cobol_code the section between ENVIRONMENT DIVISION. and PROCEDURE DIVISION
        match = re.search(r'ENVIRONMENT DIVISION\.(.*?)PROCEDURE DIVISION\.', cobol_code, re.DOTALL | re.IGNORECASE)
        if match:
            cobol_code = match.group(1)

        prompt = f"""
            Extract all data structures (01 levels, groups, elementary items) from the COBOL code below and return them in JSON format.
            Ensure the JSON is valid and only contains the data structures.    

            COBOL CODE:
        {cobol_code}
        """
        system_prompt="You are an expert COBOL programmer. "
        messages = [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt
                }
            }
        ]
        try:

            response = await ctx.sample(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.7
            )
            response_text = response.text.strip() if response.text else ""
            
            if not response_text:
                await ctx.error("Empty response from LLM")
                return "Error: Empty response from LLM"
    
            # Try to extract JSON from response if it contains extra text
            json_match = re.search(r'(\[.*\]|\{.*\})', response_text, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
            else:
                json_content = response_text
                
            # Optional: try parsing it to validate JSON
            try:
                parsed = json.loads(json_content)
                await ctx.info("Successfully parsed JSON response")
            except Exception as e:
                await ctx.warning(f"Response is not valid JSON: {e}")
                await ctx.info(f"Raw response: {response_text[:200]}...")
                parsed = response_text  # fallback

            # Register JSON result as resource - FastMCP format
            resource_uri = f"data-structure://{repository}/{filename}"
            resource_content = json.dumps(parsed, indent=2) if isinstance(parsed, (dict, list)) else str(parsed)
            
            # In FastMCP, use the mcp server instance to add resources
            resource = TextResource(
                uri=resource_uri,
                name=f"Data Structure for {filename}",
                description=f"COBOL data structures extracted from {filename}",
                text=resource_content
            )
            
            # Add to FastMCP server resources
            mcp.add_resource(resource)
            await ctx.info(f"Resource saved with URI: {resource_uri}")

            # Second LLM call to convert to pseudocode
            convert_to_pseudo_prompt = f"""
    You will receive COBOL data structures in JSON format. Each structure contains level numbers, names, and PIC clauses.

    Your task is to:
    1. Convert these structures into human-readable pseudocode (use Pascal-style RECORD/STRUCT format).
    2. For each group or field, add a short, helpful description of its likely purpose (based on name and PIC).
    3. Use consistent indentation to show hierarchy.
    4. Do not include explanations about what you are doing — just output the pseudocode with inline comments.

    Input JSON:
    {json_content}
    """
            
            pseudo_messages = [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": convert_to_pseudo_prompt
                    }
                }
            ]
            
            pseudo_response = await ctx.sample(
                messages=pseudo_messages,
                system_prompt="You are a COBOL data structure analyst.",
                temperature=0.7
            )
            pseudo_text = pseudo_response.text.strip() if pseudo_response.text else ""
            await ctx.info(f"Pseudocode response length: {len(pseudo_text)}")
            
            # Register pseudocode as another resource
            pseudo_uri = f"pseudocode://{repository}/{filename}"
            pseudo_resource = TextResource(
                uri=pseudo_uri,
                name=f"Pseudocode for {filename}",
                description=f"Human-readable pseudocode structures from {filename}",
                text=pseudo_text
            )
            
            mcp.add_resource(pseudo_resource)
            await ctx.info(f"Pseudocode resource saved with URI: {pseudo_uri}")
            
            # Return combined result
            return pseudo_text

        except Exception as e:
            await ctx.error(f"Error during LLM processing: {e}")
            return f"Error: {e}"
