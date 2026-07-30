def generate_content():
    response = client.models.generate_content(
                    model="gemini-3.6-flash",  # Gemini me generate_content ke liye sahi model use karein
                        contents=history,          # OpenAI ke 'messages' ki jagah 'contents' use hota hai
                        config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,    
                        tools=tools            # Tools ko config ke andar pass kiya jata hai
                        )
                    )
def generate_followup():
    pass
        