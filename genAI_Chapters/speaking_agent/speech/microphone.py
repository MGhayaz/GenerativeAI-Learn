import speech_recognition  as sr
from core.errors import SpeechError
recognizer = sr.Recognizer()
def record_audio()-> sr.AudioData: 
    try:
        with sr.Microphone() as mic : # mic file is open
            print("[🎙️]Speak")
            audio = recognizer.listen(mic) # actual record jahan mic open hai
            print("Processing...")
            return audio # this try has to be handled with exception 
        # because this type of error comes under Infrastructure Breakdown categorym here if we kept pydantic,
        # this will return validation error but that was not needed because when mic is not working, this system will anyway face under OS, 
        # pydantic is used when exceptions should not crash the system eg : [Expected Failures] category speech to text ,where user speech is collected again if our function fail to intrepret it
    except OSError as e :
        raise SpeechError(
            f"Microphone could not be accessed: {e}"
        ) from e    
def calibrate_microphone(duration: float = 1.0,) -> None:
    try:
        with sr.Microphone() as microphone:
            print("[🎙️] Calibrating microphone...")
            recognizer.adjust_for_ambient_noise(
                microphone,
                duration=duration,
            )
            recognizer.pause_threshold = 2.0
            print("[🎙️] Microphone calibrated.")

    except OSError as e:
        raise RuntimeError(
            f"Microphone calibration failed: {e}"
        ) from e