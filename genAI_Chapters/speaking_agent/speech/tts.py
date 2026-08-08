from llms.client import client
from config import TTS_MODEL, VOICE_NAME
import traceback
def generate_tts(final_content):
    try: # speech client exception handling
        print("creating audio through ai response")
        interaction = client.interactions.create(
        model=TTS_MODEL,
        input=f"Speak naturally and conversationally: {final_content}", # defining style and input in input feild as google specifies
        response_format={"type": "audio"}, # response type declare
        generation_config={"speech_config": [{"voice": VOICE_NAME}]} # speaker type 
        ) 
        print("ai audio created")
    except Exception as e:
        print(f"TTS error: {e}")
        traceback.print_exc()
    return interaction            
                