from llms import client
def generate_tts(final_content):
    print("creating audio through ai response")
    interaction = client.get_genai_client().interactions.create(
                    model="gemini-3.1-flash-tts-preview",
                    input=f"Speak naturally and conversationally: {final_content}", # defining style and input in input feild as google specifies
                    response_format={"type": "audio"}, # response type declare
                    generation_config={"speech_config": [{"voice": "Leda"}]} # speaker type 
                    )
    return interaction 