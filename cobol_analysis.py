from fastmcp.resources import  TextResource, resource_manager
from templates.extract_edges import extract_edges_prompt
from sampling import sample_helper


async def extract_edges(content, ctx) -> str:
    system_prompt, messages_for_llm = extract_edges_prompt(content)
    print(f"system_prompt: {system_prompt}")
    print(f"messages_for_llm: {messages_for_llm}")
    response = await sample_helper(ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0)
    print(f"response: {response}")
    return response


