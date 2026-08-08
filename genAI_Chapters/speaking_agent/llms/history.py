from google.genai import types


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
def append_tool(history , tool_response_parts):
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