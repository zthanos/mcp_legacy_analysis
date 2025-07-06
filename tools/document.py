from helpers.response_helper import graph_to_json
from templates.classify_file_template import classify_file_template
from sampling import sample_helper


def retreive_document_info(session, repository, filename):
    result = session.run("""
        MATCH (documentInfo:Document {filename: $filename})
        RETURN documentInfo
    """, filename=filename)
    document_info = graph_to_json(result, "documentInfo")
    # print(f"document_info: {document_info}")

    return document_info


async def classify_document(session, repository, filename, ctx):
    try:
        document_info = retreive_document_info(session=session, repository=repository, filename=filename)[0]
    except Exception as e:
        await ctx.error(f"Error: Unable to retrieve document info: {str(e)}")
        return "Error: Unable to retrieve document info"

    content = get_file_content_full_path(document_info["full_path"])
    try:    
        system_prompt, messages_for_llm = classify_file_template(filename=filename, content=content, repository=repository)
        response = await sample_helper(ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0)

        if not response:
            await ctx.error("Empty response from LLM")
            return "Error: Empty response from LLM"

            
        return response.strip()


    except Exception as e:
        return f"Error: Unable to classify file due to processing error: {str(e)}"        


# Helper functions

def get_file_content_full_path(full_path: str) -> str:
    with open(full_path, "r") as f:
        return f.read()

async def get_file_content(session, repository, filename, ctx) -> str:
    try:
        document_info = retreive_document_info(session=session, repository=repository, filename=filename)[0]
    except Exception as e:
        await ctx.error(f"Error: Unable to retrieve document info: {str(e)}")
        return "Error: Unable to retrieve document info"

    return get_file_content_full_path(document_info["full_path"])