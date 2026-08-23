import base64
import traceback
from speech import microphone, stt, tts, audio
from llms import history, chat
from workflow import tool_handler
from models.schemas import PendingAction
MAX_TOOL_ITERATIONS = 5

def run_conversation() -> None:
    conversation_history = []
    pending_action: PendingAction | None = None
    microphone.calibrate_microphone()
    while True:
        user_audio = microphone.record_audio()

        speech_result = stt.speech_to_text( 
            audio=user_audio
        )

        if not speech_result.success:# AGAR USER QUERY EMPTY HAI YA KOI ISSUE/FAULTY HAI TOH PHIRSE ITERATION KARAO
            print(speech_result.error)
            continue

        print(f"User: {speech_result.text}")

        if speech_result.text.lower().strip() in [
            "exit",
            "band hojao",
            "bye",
        ]:
            print(
                "Irshard V2: Acha waqt bacha raha toh phir milinge"
            )
            break

        conversation_history = history.append_user_query(
            history=conversation_history,
            user_audio_to_text=speech_result.text,
        )

        response = chat.generate_content(
            history=conversation_history
        )

        tool_iterations = 0

        while response.function_calls:
            tool_iterations += 1

            if tool_iterations > MAX_TOOL_ITERATIONS:
                raise RuntimeError(
                    "Maximum tool iteration limit exceeded."
                )
            # OUR TOOL HANDLER RETURNS A TUPLE WHICH INCLUDES A LIST - HISTORY WITH TOOLS RESPONSES AND EXCEUTIONSUMMARY WHICH MAKED DECISION FOR SUSPECIOUS/DANGER CAUSING COMMANDS
            (
                conversation_history,
                tool_summary,
            ) = tool_handler.handle_tool_calls(
                response=response,
                history=conversation_history,
            )

            if tool_summary.requires_confirmation:
                pending_action = tool_summary.pending_action

                print(
                    "⚠️ This action requires your confirmation."
                )

                break

            response = chat.generate_followup(
                history=conversation_history
            )

        if pending_action is not None:
            continue

        final_content = response.text or ""

        conversation_history = history.append_assistant(
            history=conversation_history,
            response=response,
        )

        print("🗣️ LLM:", final_content)

        interaction = tts.generate_tts(
            final_content=final_content
        )

        wav_file = audio.wave_file(
            "out.wav",
            base64.b64decode(
                interaction.output_audio.data
            ),
        )

        audio.play_audio(wav_file)  
def is_confirmation(text: str) -> bool:
    return text.lower().strip() in {
        "yes",
        "y",
        "haan",
        "ha",
        "confirm",
        "run it",
    }
def is_rejection(text: str) -> bool:
    return text.lower().strip() in {
        "no",
        "n",
        "nahi",
        "cancel",
        "stop",
    }        