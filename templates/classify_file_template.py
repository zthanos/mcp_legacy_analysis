from pathlib import Path
    
def cobol_flow_extraction(filename, content: str) -> str:
    return {
        "system_prompt": "You are an expert in programming languages and file formats, especially legacy systems including COBOL, JCL, and mainframe technologies.", 
        "llm_messages": f"""
Analyze the following file content and determine its type.

Rules:
- If it's source code, return ONLY the programming language name (e.g., "Python", "COBOL", "Java", "JavaScript", "C", "C++", "TypeScript", "CLIST", "PL/I")
- If it's not source code, return a precise file type (e.g., "JCL", "BMS Map", "Configuration", "Shell Script", "SQL Script", "Plain Text", "Data File")
- Consider both filename extension and content
- For mainframe files: JCL jobs, BMS maps, copybooks should be identified correctly
- Return ONLY the classification label, nothing else

Filename: {filename}
File extension: {Path(filename).suffix}
Content preview:
{content[:2000]}
"""
}
    