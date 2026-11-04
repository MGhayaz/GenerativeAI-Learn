from speech import microphone, stt, tts, audio
from llms import history, chat
from core.errors import LLMError
import uuid
import time
from workflow.confirmation import is_confirmation,is_rejection
from tools.executor import execute_pending_action
from database.repository import save_turn
from workflow.tool_handler import handle_tool_calls
from models.schemas import PendingAction , TurnRecord, ToolCallRecord
import logging
logger = logging.getLogger(__name__)
from core.config import settings

def run_conversation() -> None:
    conversation_id = f"conv_{uuid.uuid4().hex[:12]}" # produce a conversation id
    turn_index = 0
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

        if speech_result.text.lower().strip() in settings.chat_closure_set:
            print("🗣️LLM: Good Bye Sir")
            break
        turn_index += 1
        turn_start = len(conversation_history)   # is turn ka start
        tool_records: list[ToolCallRecord] = []
        assistant_message: str | None = None
        status = "success"
        
        
        user_text = speech_result.text
        model_input = user_text

        if pending_action is not None:
            if is_confirmation(user_text):
                started = time.perf_counter()
                result = execute_pending_action(pending_action)
                latency_ms = int((time.perf_counter() - started) * 1000)

                tool_records.append(
                    ToolCallRecord(
                        tool_name=pending_action.tool_name,
                        arguments=pending_action.arguments,
                        status="success" if result.success else "error",
                        result=(result.result or "")[:2000] or None,
                        error=(result.error or "")[:2000] or None,
                        latency_ms=latency_ms,
                    )
                )
                model_input = (
                    f"The user confirmed. The command "
                    f"`{pending_action.arguments.get('command')}` was executed. "
                    f"success={result.success}. "
                    f"Output: {(result.result or result.error or '')[:2000]}"
                )
            elif is_rejection(user_text):
                model_input = (
                    "The user declined. The pending command was NOT executed. "
                    "Acknowledge and do not retry it."
                )
            # Na confirm, na reject: naya query maan lo, pending drop
            pending_action = None
        conversation_history = history.append_user_query(
            history=conversation_history,
            user_audio_to_text=model_input, # user_text nahi
        )
        try:
            response = chat.generate_content(history=conversation_history)
            tool_iterations = 0
        
            while response.function_calls:
                
                tool_iterations += 1

                if tool_iterations > settings.max_tool_iterations:
                    raise LLMError("Tool iteration limit exceeded.")
                # OUR TOOL HANDLER RETURNS A TUPLE WHICH INCLUDES A LIST - HISTORY WITH TOOLS RESPONSES AND EXCEUTIONSUMMARY WHICH MAKED DECISION FOR SUSPECIOUS/DANGER CAUSING COMMANDS
                
                conversation_history, tool_summary = handle_tool_calls(
                    response=response,history=conversation_history,
                )
                tool_records.extend(tool_summary.records)   # Agar LLM 2 baar tools call ke iterations kara toh second iteration ke time pehle iteration ke records accumulate kare

                if tool_summary.requires_confirmation:
                    pending_action = tool_summary.pending_action
                    status = "awaiting_confirmation"
                    break

                response = chat.generate_followup(history=conversation_history)
            if status != "awaiting_confirmation":
                assistant_message = response.text or ""
                conversation_history = history.append_assistant(
                    history=conversation_history, response=response
                )
                if any(r.status == "error" for r in tool_records):
                    status = "partial_failure"
        except LLMError:
            status = "failed"
        except Exception:
            logger.exception("Unexpected failure in turn")
            status = "failed"   
        if status == "awaiting_confirmation" and pending_action is not None:
            assistant_message = (
                f"I need your confirmation before running: "
                f"{pending_action.arguments.get('command')}. Say yes to proceed or no to cancel."
            )
            conversation_history = history.append_model_text(conversation_history, assistant_message)    
        turn_contents = conversation_history[turn_start:]     
        if status == "failed":
            del conversation_history[turn_start:]
        save_turn(TurnRecord( # database is storing following values, mongodb, collection name "turns"
            conversation_id=conversation_id,
            turn_index=turn_index,
            user_message=speech_result.text,
            tool_calls=tool_records,
            assistant_message=assistant_message,
            status=status,
            model=settings.model_name,
            llm_contents=[
                c.model_dump(mode="json", exclude_none=True)
                for c in turn_contents
            ],
        ))

        if status =="failed": 
            continue                

        # final_content = response.text or ""
        final_content = assistant_message or ""
        if not final_content:
            continue
        print("🗣️ LLM:", final_content)
        tts_result = tts.generate_tts(
            final_content=final_content
        )
        if not tts_result.success:
            print(f"TTS error: {tts_result.error}")
            continue

        audio_file = audio.create_temp_wav(
            pcm=tts_result.audio_data
        )
        try:
            audio.play_audio(audio_file)
        finally:
            audio_file.unlink(missing_ok=True) # whether the temporary file is played or not, delete it
           
