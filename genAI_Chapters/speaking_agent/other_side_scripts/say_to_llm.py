from dotenv import load_dotenv
load_dotenv()
import speech_recognition  as sr
recorgnize = sr.Recognizer()
from google import genai
client = genai.Client()
SYSTEM_PROMPT = """
YOU ARE AN AGENT WHICH TALKS LIKE AN VOICE ASSISTANT, YOU ARE LIABLE TO MAKE RESPONSES IN A TALKING WAY
"""
if input("Press [S] to record: ").strip().lower() == "s":
    with sr.Microphone() as mic : # mic file is open
        recorgnize.adjust_for_ambient_noise(mic) # clearity ke liye mic ku background noise se bachaye
        recorgnize.pause_threshold = 2
        print("Please Speak")
        audio = recorgnize.listen(mic) # actual record
        print("Processing...")
        user_audio_to_text = recorgnize.recognize_google(audio)
        print("User:", user_audio_to_text)


        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=user_audio_to_text,
            config={
                "system_instruction":SYSTEM_PROMPT,
            },
        )
        print("LLM:", response.text)
else :
    print("no worries ethan, this message will get deleted in next 5 minutes 💣😎")        