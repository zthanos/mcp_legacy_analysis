from ast import Dict
import re

from pydantic.json_schema import JsonSchemaMode
from helpers.response_helper import graph_to_json, safe_extract_json
from templates.classify_document_template import classify_document_template
from sampling import sample_helper
from graph.graph_query import (
    get_documents_by_repository as get_documents_query,
    get_document_details,
)
from utils.utils import (
    safe_read_file,
    get_file_content,
)
from prompts.code_analysis_prompt import (
    prepare_document_analysis_prompt,
    processed_data_to_json,
)


def retreive_document_info(session, repository, filename):
    result = session.run(
        """
        MATCH (documentInfo:Document {filename: $filename})
        RETURN documentInfo
    """,
        filename=filename,
    )
    document_info = graph_to_json(result, "documentInfo")
    # print(f"document_info: {document_info}")

    return document_info


async def classify_document(session, repository, filename, ctx):
    try:
        document_info = retreive_document_info(
            session=session, repository=repository, filename=filename
        )[0]
    except Exception as e:
        await ctx.warning(f"Warning: File not found in db: {str(e)}")
        
    content = get_file_content(repository, filename)


    try:
        system_prompt, messages_for_llm = classify_document_template(
            filename=filename, content=content, repository=repository
        )
        response = await sample_helper(
            ctx=ctx,
            messages_for_llm=messages_for_llm,
            system_prompt=system_prompt,
            temperature=0,
        )
        print(response)

        if not response:
            await ctx.error("Empty response from LLM")
            return "Error: Empty response from LLM"

        return safe_extract_json(response.strip())


    except Exception as e:
        return f"Error: Unable to classify file due to processing error: {str(e)}"


# Helper functions


def get_document_content_full_path(full_path: str) -> str:
    with open(full_path, "r") as f:
        return f.read()


async def get_document_content(session, repository, filename, ctx) -> str:
    try:
        document_info = retreive_document_info(
            session=session, repository=repository, filename=filename
        )[0]
    except Exception as e:
        await ctx.error(f"Error: Unable to retrieve document info: {str(e)}")
        return "Error: Unable to retrieve document info"

    return get_document_content_full_path(document_info["full_path"])


def get_documents_by_repository(session, repository_name: str):
    json_data = get_documents_query(session, repository_name)
    return graph_to_json(json_data, "documentInfo")


async def document_analysis(session, repository_name, filename: str, ctx) -> str:
    # Locate Document

    # Read Document Content
    content = get_file_content(repository_name, filename)
    if not content:
        error_str = f"Error: Skipping unreadable file: {filename}"
        await ctx.error(error_str)
        return error_str

    document_info = await classify_document(session, repository_name, filename, ctx)

    if not isinstance(document_info, dict):
        await ctx.error(f"Invalid classify_document response: {document_info}")
        return f"Error: Invalid classify_document response"

    language = document_info.get("language")
    if not language:
        await ctx.error("Missing language in classify_document response")
        return "Error: Missing language in classify_document response"

    # Prepare analysis prompt
    llm_prompt, system_prompt = prepare_document_analysis_prompt(
        source_code=content,
        filename=filename,
        repository_name=repository_name,
        program_id=filename,
        language=language,
    )

    # Send prompt to LLM
    response = await sample_helper(
        ctx=ctx, messages_for_llm=llm_prompt, system_prompt=system_prompt, temperature=0
    )
    print(f"system_prompt: {system_prompt}")
    print(f"messages_for_llm: {llm_prompt}")
    await ctx.debug(f"response: {response}")
    if not response:
        await ctx.error("Empty response from LLM")
        return "Error: Empty response from LLM"
    print(f"response: {response}")

    # Send response to LLM for json transformation
    response = await sample_helper(
        ctx=ctx, messages_for_llm=response, system_prompt=system_prompt, temperature=0
    )
    await ctx.debug(f"response: {response}")

    # Generalize LLM analysis to JSON
    json_response = processed_data_to_json(response)

    match = re.search(r"```json\s*([\s\S]*?)\s*```", json_response)
    if match:
        json_str = match.group(1).strip()
        await ctx.debug(json_str)
        return json_str

    return json_response
