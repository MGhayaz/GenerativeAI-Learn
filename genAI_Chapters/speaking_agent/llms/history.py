import json
from google.genai import types

def contents_from_docs(docs: list[dict]) -> list[types.Content]:
    """DB mein stored llm_contents (JSON dicts) ko wapas types.Content banata hai.

    JSON-mode validation isliye: bytes fields (thought_signature) base64 se
    sahi decode hon. Python-mode validate string ko seedha bytes bana sakta hai,
    jisse signature kharab ho jaata hai. Test isi ko verify karta hai.
    """
    return [types.Content.model_validate_json(json.dumps(doc)) for doc in docs]

def append_user_query(
    history: list[types.Content],
    user_audio_to_text: str,
    ) -> list[types.Content]:
    history.append(
        types.Content(
            role="user",
            parts=[
                types.Part(text=user_audio_to_text)
            ],
        )
    )

    return history
def append_tool(history , tool_response_parts): # tool_response_parts ko history mein add karna, taaki Gemini ko pata chale ki tool call hua tha aur uska response kya tha.
    history.append(
                        types.Content(
                            role="user", # gemini takes tools details as user
                            parts=tool_response_parts
                        )
                    )
    return history

def append_assistant(
    history: list[types.Content],
    response,
) -> list[types.Content]:
    history.append(response.candidates[0].content)
    return history
    
def clear(history: list[types.Content]) -> None:
    history.clear()  
    
def append_model_text(history: list[types.Content], text: str) -> list[types.Content]:
    history.append(types.Content(role="model", parts=[types.Part(text=text)]))
    return history    