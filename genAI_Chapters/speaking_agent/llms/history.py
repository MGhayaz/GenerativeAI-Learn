from google.genai import types
history: list[types.Content] = []

def append_user(user_audio_to_text):
    history.append( # apending or storing context in list typed dict, here our query is being stored
                            types.Content(
                                role="user", 
                                    parts=[
                                        types.Part(text=user_audio_to_text) 
                                    ]
                            )
                        )
    return history
def append_tool(tool_response_parts):
    history.append(
                        types.Content(
                            role="user", # gemini takes tools details as user
                            parts=tool_response_parts
                        )
                    )
    return history

def append_assistant(response):
    history.append(response.candidates[0].content)
    return history
    
def clear():
      history.pop()  