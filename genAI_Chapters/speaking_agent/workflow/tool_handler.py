import traceback
from pydantic import ValidationError
from llms import history as his
from tools_unit import registry
def function_handler(response , history):
    tool_call_count = 0
    while function_calls: # threshold limit 5, 5se zyada baar tools call nahi in each loop traversal
        tool_call_count += 1
        if tool_call_count > 5:
            break
        # 1. Assistant ka function call response history me add karein (Gemini automatically requires the original function_call parts in history)
        # Note: Agar initial response directly models.generate_content se aaya hai, 
        # toh response.candidates[0].content ko aap seedhe history me append kar sakte hain.
        history = his.append_assistant(response)
        
        # Tool responses ko store karne ke liye list
        tool_response_parts = []
        
        # 2. Saare function calls ko execute karein
        for tool_call in function_calls:
            function_name = tool_call.name
            tool_info = registry.TOOL_MAP.get(function_name)
            if tool_info is None: # just ek double check ki ye tool map ke value khali toh nahi hai ya galat toh nahi hai
                break
            
            # Gemini arguments directly dict (Python object) hote hain, json string nahi
            try:
                arguments = tool_info["schema"].model_validate(tool_call.args)
            except ValidationError as e:
                print(f"Validation failed: {e}")
                    # Yahan apna error handling code likhein (e.g., return, log, ya default values)
                arguments = None
                traceback.print_exc()
            try:
                result = tool_info["function"](**arguments.model_dump())
            except Exception as e:
                result = str(e)
                traceback.print_exc()
            
            
            # Gemini format me function ka result part banayein
            # result ko string ya dict format me pass karein
            tool_response_parts.append(
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": str(result)}  
                )
            )
        
        # 3. Tool ke saare results ko 'user' role ke saath history me append karein
        history.append(
            types.Content(
                role="user", # gemini takes tools details as user
                parts=tool_response_parts
            )
        )
        
        # 4. Agla tool execution ya final reply lene ke liye model ko dobara call karein
        try:
            print("[function unit] final response creation")
            response = client.models.generate_content(
                model="gemini-3.6-flash", # Sahi stable model identifier use karein
                contents=history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=tools
                )
            )
            # Agle loop ke liye check karein ki kya model fir se tool call karna chahta hai
            function_calls = response.function_calls
            
        except Exception as ew:
            print(ew)
            traceback.print_exc()
            break