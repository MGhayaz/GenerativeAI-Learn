from speech import tts, audio,microphone,stt
from llms import history,chat
from workflow import tool_handler
import traceback, types
history_log: list[types.Content] = []
try :
    while True:
        user_query = stt.speech_to_text(audio= microphone.Recognizer() )
        print(f"User: ", user_query)
        if user_query.lower().strip() in ["exit", "band hojao","bye"]:
            print("Irshard V2: Acha waqt bacha raha toh phir milinge")
            break
        history_log = history.append_user_query( history=history_log,user_audio_to_text= user_query )
        
        response = chat.generate_content(history=history_log)
        final_content = tool_handler.function_handler(response=response , history_log=history_log)
        audio_data = tts.generate_tts(final_content)
        print("🗣️LLM:", final_content)
        
        print("playing ai audio")
        wav_file = audio.wave_file(
            "out.wav",
            audio_data
        )
        try:
            audio.play_audio("out.wav")
        except RuntimeError as e:
            print(e)
        history_log = history.append_assistant(response=response)
        print("llm response appended")
        print("Loop completed peacefully ")
except Exception as e : # mega try catch
        traceback.print_exc()