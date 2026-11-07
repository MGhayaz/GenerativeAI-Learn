from llms.client import get_client
from core.config import settings
from models.schemas import TTSResult 
import base64

def generate_tts(final_content)-> bytes:
    try:
        
        print("creating audio through ai response")
        interaction = get_client().interactions.create(
            model=settings.tts_model,
            input=f"Speak like a Indian man speaking English: {final_content}", # defining style and input in input feild as google specifies
            response_format={"type": "audio"}, # response type declare
                generation_config={
                "speech_config": [{"voice": settings.voice_name}]
                } # speaker type 
        )
        print("ai audio created")
        output_audio = interaction.output_audio
        if output_audio is None or not output_audio.data:
            return TTSResult(
                success=False,
                error="TTS returned no audio data",
            )

        return TTSResult(
            success=True,
            audio_data=base64.b64decode(output_audio.data, validate=True),
        )
    except  Exception as e :
        return TTSResult(
            success=False,
            error=f"TTS generation failed: {e}"
        )   