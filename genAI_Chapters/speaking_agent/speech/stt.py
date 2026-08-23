import speech_recognition as sr # intrepreter
from models.schemas import SpeechResult # pydantic
from speech.microphone import recorgnize # speak se text banata

def speech_to_text(audio):
    try: # unknown input exception block
        print("making speech to text for LLM")
        text =  recorgnize.recognize_google(audio) # this particular call make text from speech so that i can give it to llm
        return SpeechResult(
            success=True,
            text=text.strip(),
        )
    except sr.UnknownValueError:
        SpeechResult(
            success=False,
            error="Samajh nahi aaya, phir bol..."
        )
    except sr.RequestError as e: 
        SpeechResult(
            success=False,
            error=f"Speech API error: {e}"
        )
        