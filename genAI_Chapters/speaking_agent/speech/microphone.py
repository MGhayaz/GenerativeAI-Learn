import speech_recognition  as sr
recorgnize = sr.Recognizer()
def Recognizer():
    with sr.Microphone() as mic : # mic file is open
        print("[🎙️]Speak")
        audio = recorgnize.listen(mic) # actual record jahan mic open hai
        print("Processing...")
        return audio
def ambient_noise():
    with sr.Microphone() as mic:
        recorgnize.adjust_for_ambient_noise(mic)
        pause_threshold()       
def pause_threshold():
        recorgnize.pause_threshold = 2