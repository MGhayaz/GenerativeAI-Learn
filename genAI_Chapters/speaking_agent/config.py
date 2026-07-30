from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types
client = genai.Client()

MODEL_NAME = "gemini-3.6-flash"
TTS_MODEL = "gemini-3.1-flash-tts-preview"
VOICE_NAME = "Leda"
WORKING_DIRECTORY = "C:\Users\moham\Downloads\Development\GenerativeAI\genAi_Chapters\speaking_agent"