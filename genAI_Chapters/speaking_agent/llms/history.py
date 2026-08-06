from google.genai import types
history: list[types.Content] = []

def append_user_query(user_audio_to_text):
    history.append( # apending or storing context in list typed dict, here our query is being stored
                            types.Content(
                                role="user", 
                                    parts=[
                                        types.Part(text=user_audio_to_text) 
                                    ]
                            )
                        )
    print("query registered in history")
    return history
def append_tool(history , tool_response_parts):
    history.append(
                        types.Content(
                            role="user", # gemini takes tools details as user
                            parts=tool_response_parts
                        )
                    )
    return history

def append_assistant(response):
    history.append(response.candidates[0].content)
    print("Loop completed peacefully ")
    return history
    
def clear():
      history.pop()  