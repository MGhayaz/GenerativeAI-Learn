import base64
import traceback
from speech import microphone, stt, tts, audio
from llms import history, chat
from workflow import tool_handler
from models.schemas import PendingCommand
MAX_TOOL_ITERATIONS = 5

def run_conversation() -> None:
    conversation_history = []
    pending_command: PendingCommand | None = None

    while True:
        user_audio = microphone.Recognizer()

        user_text = stt.speech_to_text(
            audio=user_audio
        )

        if not user_text: # AGAR USER QUERY EMPTY HAI TOH PHIRSE ITERATION KARO
            continue

        print(f"User: {user_text}")

        if user_text.lower().strip() in [
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
            user_audio_to_text=user_text,
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
                pending_command = tool_summary.pending_command

                print(
                    "⚠️ This action requires your confirmation."
                )

                break

            response = chat.generate_followup(
                history=conversation_history
            )

        if pending_command is not None:
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