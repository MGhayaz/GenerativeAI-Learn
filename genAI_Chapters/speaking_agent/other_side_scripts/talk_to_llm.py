from dotenv import load_dotenv
load_dotenv()
import speech_recognition  as sr
import simpleaudio as sa
recorgnize = sr.Recognizer()
from google import genai
from google.genai import types
import wave  # raw PCM audio bytes ku proper .wav audio file banata
import base64 # API audio bytes ku Base64 text me bhejti, ye usku wapas original audio bytes me decode karta
client = genai.Client() # client to interact and create response for both, llm and tts model
# pre declaration to system
SYSTEM_PROMPT = """ 
YOU ARE AN AGENT WHICH TALKS LIKE AN VOICE ASSISTANT, YOU ARE LIABLE TO MAKE RESPONSES IN A TALKING WAY
YOUR RESPONSE IS LATER CONVERTED INTO VOICE, SO MAKE SURE IT HAS HUMAN TOUCH AS MUCH AS POSSIBLE
"""
chat_history: list[dict[str, str]] = []
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2): # node for tts
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm) 
def play_audio(filename): # node/function for audio play, it takes the audio which are combinations of alphabets [thats how audio is written]
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()         
while(True):    
    with sr.Microphone() as mic : # mic file is open
        recorgnize.adjust_for_ambient_noise(mic) # clarity ke liye mic ku background noise se bachaye
        recorgnize.pause_threshold = 2 # here this wait for two seconds to accumulate audio
        print("[🎙️]Speak")
        audio = recorgnize.listen(mic) # actual record jahan mic open hai
        print("Processing...")
        try: # unknown input exception block
            user_audio_to_text = recorgnize.recognize_google(audio) # this particular call make text from speech so that i can give it to llm
        except sr.UnknownValueError:
            print("Samajh nahi aaya, phir bol...")
            continue
        except sr.RequestError as e: 
            print(f"Speech API error: {e}")
            continue
        print("User:", user_audio_to_text)
        if user_audio_to_text.lower().strip() in {"exit", "bye", "stop"}: # for check out
            print("acha waqt bacha raha toh phir milinge...")
            break    
        chat_history.append( # apending or storing context in list typed dict, here our query is being stored
            types.Content(
                role="user", 
                    parts=[
                        types.Part(text=user_audio_to_text) 
                    ]
            )
        )
        try: # client side exception handling
            response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=chat_history,
            config={"system_instruction": SYSTEM_PROMPT},
        )
        except Exception as e:
            print(f"LLM error: {e}")
            continue
        chat_history.append( # append the LLM response as our query
            types.Content(
                role="model", #predefined name "model" which entity the llm while revision
                    parts=[
                        types.Part(text=response.text)
                    ]
            )
        )
        try: # speech client exception handling
            interaction = client.interactions.create(
            model="gemini-3.1-flash-tts-preview",
            input=f"Speak naturally and conversationally: {response.text}", # defining style and input in input feild as google specifies
            response_format={"type": "audio"}, # response type declare
            generation_config={"speech_config": [{"voice": "Leda"}]} # speaker type 
        )
        except Exception as e:
            print(f"TTS error: {e}")
            continue
        print("🗣️LLM:", response.text)
        wave_file('out.wav', base64.b64decode(interaction.output_audio.data))
        try:
            play_audio('out.wav')
        except Exception as e:
            print(f"Playback error: {e}")
            