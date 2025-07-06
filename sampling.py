async def sample_helper(ctx, messages_for_llm: str, system_prompt: str, temperature: float = 0.7, json_output: bool = False) -> str:
    """
    This function is a placeholder for sampling-related functionality.
    It currently does not perform any operations but can be extended in the future.
    """
    try:
        messages = [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"{system_prompt}\n\n{messages_for_llm}",
                }
            }
        ]
        
        prefs = None
        if json_output:
            prefs = {"response_format": {"type": "json_object"}}
        await ctx.debug(f"Sampling. Calling LLM for flow extraction: {messages}")
        response = await ctx.sample(
            messages=messages,
            temperature=temperature,
            model_preferences=prefs
        )
            
        return response.text.strip() if response.text else ""
    except Exception as e:
        await ctx.error(f"Sampling. Error calling LLM: {e}")
        
        return f"Sampling. Error calling LLM: {e}"            