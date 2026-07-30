def speech_to_text():
    try: # unknown input exception block
                print("making speech to text for LLM")
                user_audio_to_text = recorgnize.recognize_google(audio) # this particular call make text from speech so that i can give it to llm
            except sr.UnknownValueError:
                print("Samajh nahi aaya, phir bol...")
                continue
            except sr.RequestError as e: 
                print(f"Speech API error: {e}")
                continue