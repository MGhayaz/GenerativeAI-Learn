from speech import microphone,stt
from llms import history , chat
from workflow import tool_handler
while True:
    user_audio_to_text = stt.speech_to_text(audio= microphone.Recognizer() )
    print("User:", user_audio_to_text)
    if user_audio_to_text.lower().strip() in ["exit", "band hojao","bye"]:
        print("Irshard V2: Acha waqt bacha raha toh phir milinge")
        break
    history_log = history.append_user_query( user_audio_to_text= user_audio_to_text )
    print("query registered in history")
    response = chat.generate_content(history=history_log)
    tool_handler.function_handler(response=response , history_log=history_log)
    