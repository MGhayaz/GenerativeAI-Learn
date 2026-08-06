from speech import microphone,stt, tts,audio
from llms import history,chat
from workflow import tool_handler
import base64 

while True:
    user_audio_to_text = stt.speech_to_text(audio= microphone.Recognizer() )
    print(f"User: ", user_audio_to_text)
    if user_audio_to_text.lower().strip() in ["exit", "band hojao","bye"]:
        print("Irshard V2: Acha waqt bacha raha toh phir milinge")
        break
    history_log = history.append_user_query( user_audio_to_text= user_audio_to_text )
    
    response = chat.generate_content(history=history_log)
    final_content = tool_handler.function_handler(response=response , history_log=history_log)
    interaction = tts.generate_tts(final_content=final_content)
    print("🗣️LLM:", final_content)
    
    print("playing ai audio")
    wav_file = audio.wave_file('out.wav', base64.b64decode(interaction.output_audio.data))
    audio.play_audio(wav_file)
    history_log = history.append_assistant(response=response)