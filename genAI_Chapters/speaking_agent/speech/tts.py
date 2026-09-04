from llms.client import client
from core.config import settings
from models.schemas import TTSResult 


def generate_tts(final_content)-> bytes:
    try:
        
        print("creating audio through ai response")
        interaction = client.interactions.create(
            model=settings.tts_model,
            input=f"Speak naturally and conversationally: {final_content}", # defining style and input in input feild as google specifies
            response_format={"type": "audio"}, # response type declare
                generation_config={
                "speech_config": [{"voice": settings.voice_name}]
                } # speaker type 
        )
        print("ai audio created")
        return TTSResult(
            success=True,
            audio_data=interaction.output_audio.data
        )
    except  Exception as e :
        return TTSResult(
            success=False,
            error=f"TTS generation failed: {e}"
        )   