import asyncio
import json
from ollama import Client as OllamaClient
from fastmcp import Client, FastMCP
from fastmcp.client.sampling import (
    SamplingMessage,
    SamplingParams,
)
from mcp.shared.context import RequestContext
from tabulate import tabulate
#In-Memory server
server = FastMCP()


ollama_client = OllamaClient(host='http://localhost:11434')

async def sampling_handler(
    messages: list,
    params,
    context,
    model="deepseek-coder:latest",
) -> str:
    
    prompt = ""
    if params.systemPrompt:
        prompt += f"{params.systemPrompt}\n\n"
    for m in messages:
        prompt += f"{m.role}: {m.content.text}\n"
    prompt += "\nReturn your answer as a JSON object."

    response = ollama_client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={'temperature': 0}
    )

    return response['message']['content']

# client = Client(server)
#HTTP Server
client = Client("http://localhost:9000/sse", sampling_handler=sampling_handler)

# client = Client("main.py")

async def workflow(client: Client):
    print("Fetching repository")
    repo_url = "https://github.com/mainframed/DOGECICS.git"
    # result = await client.call_tool("fetch_repository", {"repo_url": repo_url})
    
    # repository_name = result[0].text
    repository_name = "DOGECICS"
    
    files_in_repository = await client.call_tool("processed_repository", {"repository": repository_name})
    data = json.loads(files_in_repository[0].text)
    table = tabulate(data, headers=["id", "repository", "full_path", "filename", "language", "classification"], tablefmt="github")
    print(table)

    maps = await client.call_tool("get_map_files", {"repository": repository_name})
    maps_data = json.loads(maps[0].text)
    print(maps_data)
    maps_table = tabulate(maps_data, headers=["id", "repository", "full_path", "filename", "language", "classification"], tablefmt="github")
    print(maps_table)


    # resources = await client.list_resources()
    # for resource in resources:
    #     print(resource)



  

async def main():
    async with client:
        await client.ping()
        await workflow(client)

        # tools = await client.list_tools()
        # for tool in tools:
        #     print(f'Tool: {tool.name}\n description {tool.description}')
        # prompts  = await client.list_prompts()
        # for prompt in prompts:
        #     print(prompt)




asyncio.run(main())