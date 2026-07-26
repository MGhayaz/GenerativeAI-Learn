from dotenv import load_dotenv
load_dotenv()
import speech_recognition  as sr
recorgnize = sr.Recognizer()
from google import genai
client = genai.Client()
SYSTEM_PROMPT = """
YOU ARE AN AGENT WHICH TALKS LIKE AN VOICE ASSISTANT, YOU ARE LIABLE TO MAKE RESPONSES IN A TALKING WAY
"""
with sr.Microphone() as mic : # mic file is open
    recorgnize.adjust_for_ambient_noise(mic) # clearity ke liye mic ku background noise se bachaye
    recorgnize.pause_threshold = 2
    print("Welcome")
while(True):    
    audio = recorgnize.listen(mic) # actual record
    print("Processing...")
    user_audio_to_text = recorgnize.recognize_google(audio)
    print("User:", user_audio_to_text)
    if(user_audio_to_text.lower().strip() != "exit", "bye", "stop"):
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=user_audio_to_text,
            config={
                "system_instruction":SYSTEM_PROMPT,
            },
        )
        print("LLM:", response.text)
            