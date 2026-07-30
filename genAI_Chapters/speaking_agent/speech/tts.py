def generate_tts():
    interaction = client.interactions.create(
                    model="gemini-3.1-flash-tts-preview",
                    input=f"Speak naturally and conversationally: {final_content}", # defining style and input in input feild as google specifies
                    response_format={"type": "audio"}, # response type declare
                    generation_config={"speech_config": [{"voice": "Leda"}]} # speaker type 
                    )
    return interaction 