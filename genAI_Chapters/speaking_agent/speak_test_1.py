import speech_recognition  as sr
recorgnize = sr.Recognizer()

with sr.Microphone() as mic : # mic file is open
    recorgnize.adjust_for_ambient_noise(mic) # clearity ke liye call kare
    recorgnize.pause_threshold = 2
    
    print("panel for mic is open, please speak")
    audio = recorgnize.listen(mic) # actual record
    print("Processing...")
    stt = recorgnize.recognize_google(audio) # audio ku speech me convert kare taki print kar sakna
    print("> ",stt)


