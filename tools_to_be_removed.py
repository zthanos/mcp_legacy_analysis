

#### To be Removed

@mcp.tool(name="processed_repository", description="Returns a list of file from a processed repository by name.")
async def processed_repository(repository: str, ctx: Context) -> list[dict]:
    files_in_repository = get_repository(session=session, repository_name=repository)
    print(f"files_in_repository: {files_in_repository}")
    return files_in_repository


@mcp.tool(name="get_map_files", description="Returns a list of map files from a processed repository by name.")
async def get_map_files(repository: str, ctx: Context) -> str:
    # response = get_repository_by_classification("BMS Map", repository)
    # await ctx.info(f"Analyzing {len(response)} map files...")
    # analyzed_data = await analyze_map("workspace\\DOGECICS\\BMS\\DOGEDMAP", ctx)
    analyzed_data =  await extract_document_flow(
        mcp=mcp,
        repository=repository,
        filename="workspace\\DOGECICS\\COBOL\\DOGEMAIN",
        classification="COBOL",
        ctx=ctx,
    )    
    print(f"analyzed_data: {analyzed_data}")
    # maps_data = json.loads(response)
    # for map in maps_data:
    #    analyzed_data = await analyze_map(map, ctx) 

    return analyzed_data    


@mcp.tool(name="extract_flow", description="Extracts the execution flow of a program, starting from its primary entry point, and returns it in a structured JSON format.")
async def extract_flow(repository: str, filename: str, ctx: Context) -> str:
    await ctx.info(f"Extracting flow for {filename} in {repository}")
    document_info = retreive_document_info(session=session, repository=repository, filename=filename)
    print(f"document_info: {document_info}")
    if len(document_info) == 0:
        return "No document info found"
    analyzed_data =  await extract_document_flow(
        mcp=mcp,
        repository=repository,
        filename=document_info[0]["full_path"],
        classification=document_info[0]["language"],
        ctx=ctx,
    )    
    print(f"analyzed_data: {analyzed_data}")
    return analyzed_data



@mcp.tool(name="find_copy_definition", description="Searches all files for a COBOL COPY label (e.g. DOGEDT) and returns the first file that contains it.")
def find_copy_definition(ctx: Context, resource_uri: str, copy_name: str) -> dict:
    import re
    # ctx.log.info(f"Searching for COPY definition: {copy_name} in {resource_uri}")
    repo_alias = resource_uri.replace("resource://", "")
    base_path = WORKSPACE / repo_alias

    matched_files = []

    # Traverse all files like list_cobol_files does
    for file_path in base_path.rglob("*"):
        # ctx.log.info(f"Checking file: {file_path}")
        if not file_path.is_file():
            continue
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
               for line in f:
                    # Look for a line that starts with the copy_name (label-style)
                    if re.match(rf"^\s*{re.escape(copy_name)}\b", line):
                        matched_files.append({
                            "copy_name": copy_name,
                            "path": str(file_path.relative_to(base_path)),
                            "line": line.strip()
                        })
                        break  # stop after first match in file
        except Exception:
            continue  # skip unreadable files

    if matched_files:
        return {
            "status": "found",
            "matches": matched_files
        }
    else:
        return {
            "status": "not_found",
            "message": f"No definition for '{copy_name}' found."
        }


@mcp.tool("get_language_specific_prompt", description="Returns the language-specific prompt for the given language.")
async def get_language_specific_prompt(language: str, source_code: str, repository_name: str, filename: str, ctx: Context) -> dict:
    system_prompt, llm_prompt = flow_extraction(
        source_code=source_code,
        filename=filename,
        repository_name=repository_name,
        program_id=filename,
        language=language
    )

    return {
        "system_prompt": system_prompt,
        "llm_prompt": llm_prompt
    }    


######################