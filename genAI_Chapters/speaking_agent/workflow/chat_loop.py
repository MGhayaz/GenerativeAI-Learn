import uuid
import time
import logging
from google.genai import types
from core.config import settings
from core.errors import LLMError
from database.repository import save_turn
from llms import history, chat
from llms.context import ConversationState , build_context
from llms.usage import compute_footprint, sum_usage
from models.schemas import PendingAction , TurnRecord, ToolCallRecord,LLMCallRecord
from speech import microphone, stt, tts, audio
from tools.executor import execute_pending_action
from tools.limiter import cap_text
from workflow.confirmation import is_confirmation,is_rejection
from workflow.tool_handler import handle_tool_calls

logger = logging.getLogger(__name__)

def run_conversation() -> None:
    conversation_id = f"conv_{uuid.uuid4().hex[:12]}" # produce a conversation id
    turn_index = 0
    state = ConversationState(conversation_id=conversation_id)
    pending_action: PendingAction | None = None
    microphone.calibrate_microphone()
    while True:
        user_audio = microphone.record_audio()
        speech_result = stt.speech_to_text(audio=user_audio)

        if not speech_result.success:# AGAR USER QUERY EMPTY HAI YA KOI ISSUE/FAULTY HAI TOH PHIRSE ITERATION KARAO
            print(speech_result.error)
            continue

        print(f"User: {speech_result.text}")

        if speech_result.text.lower().strip() in settings.chat_closure_set:
            print("🗣️LLM: Good Bye Sir")
            break
        # geninune turn ka start
        turn_index += 1
        current: list[types.Content] = []  # sirf is turn ke contents   
        tool_records: list[ToolCallRecord] = []
        llm_calls: list[LLMCallRecord] = []
        failure_reason: str | None = None
        assistant_message: str | None = None
        status = "success"
        
        
        user_text = speech_result.text
        model_input = user_text

        if pending_action is not None:
            if is_confirmation(user_text):
                started = time.perf_counter()
                result = execute_pending_action(pending_action)
                latency_ms = int((time.perf_counter() - started) * 1000)
                raw_output = result.result or result.error or ""
                tool_records.append(
                    ToolCallRecord(
                        tool_name=pending_action.tool_name,
                        arguments=pending_action.arguments,
                        status="success" if result.success else "error",
                        result=(result.result or "")[:2000] or None,
                        error=(result.error or "")[:2000] or None,
                        latency_ms=latency_ms,
                        output_chars=len(raw_output),
                        truncated=len(raw_output) > settings.max_tool_output_chars,
                    )
                )
                output_text = cap_text(
                    raw_output,
                    settings.max_tool_output_chars,
                ).text
                model_input = (
                    f"The user confirmed. The command "
                    f"`{pending_action.arguments.get('command')}` was executed. "
                    f"success={result.success}. "
                    f"Output: {output_text}"
                )
            elif is_rejection(user_text):
                model_input = (
                    "The user declined. The pending command was NOT executed. "
                    "Acknowledge and do not retry it."
                )
            # Na confirm, na reject: naya query maan lo, pending drop
            pending_action = None
        current = history.append_user_query( # current mein user ka query append karna, aur history mein bhi add karna
            history=current,
            user_audio_to_text=model_input,
        )
        # context turn ke start pe EK baar banta hai, poore turn ke liye same (freeze rule)
        built = build_context(state) # built.contents mein poore conversation ka history hai, built.turns_included mein kitne turns included hai
        logger.info(
            "Context built: %d turns, %d contents",
            built.turns_included,
            len(built.contents),
        )
        try:
            response, call = chat.generate_content(history=built.contents + current,iteration=1) # purpose: LLM se response generate karna, aur call record bhi return karna
            llm_calls.append(call)
            tool_iterations = 0
        
            while response.function_calls:
                
                tool_iterations += 1

                if tool_iterations > settings.max_tool_iterations:
                    raise LLMError("Tool iteration limit exceeded.")
                # OUR TOOL HANDLER RETURNS A TUPLE WHICH INCLUDES A LIST - HISTORY WITH TOOLS RESPONSES AND EXCEUTIONSUMMARY WHICH MAKED DECISION FOR SUSPECIOUS/DANGER CAUSING COMMANDS
                
                current, tool_summary = handle_tool_calls(response=response, history=current) # pehle poori history jaati thi, ab sirf current. Ye apne andar current mein append karke wahi list return karta hai.
                tool_records.extend(tool_summary.records)   # Agar LLM 2 baar tools call ke iterations kara toh second iteration ke time pehle iteration ke records accumulate kare

                if tool_summary.requires_confirmation:
                    pending_action = tool_summary.pending_action
                    status = "awaiting_confirmation"
                    break

                response, call = chat.generate_followup(
                history=built.contents + current,
                iteration=tool_iterations + 1,
                )
                llm_calls.append(call)
                
            if status != "awaiting_confirmation":
                assistant_message = response.text or ""
                current = history.append_assistant(history=current, response=response)
                if any(r.status == "error" for r in tool_records):
                    status = "partial_failure"
        except LLMError as exc:
            status = "failed"
            failure_reason = f"LLMError: {exc}"[:300]
        except Exception as exc:
            logger.exception("Unexpected failure in turn")
            status = "failed"   
            failure_reason = f"{type(exc).__name__}: {exc}"[:300]
        if status == "awaiting_confirmation" and pending_action is not None:
            assistant_message = (
                f"Final Call for: "
                f"{pending_action.arguments.get('command')}. Say yes to proceed or no to cancel."
            )
            current = history.append_model_text(current, assistant_message)    
        turn_contents = current
        usage_totals = sum_usage(llm_calls) if llm_calls else None

        footprint_tokens: int | None = None
        footprint_source: str | None = None
        if status != "failed" and llm_calls: # Agar turn failed hai toh footprint ka calculation nahi karna, kyuki agar LLM call fail hua toh uska usage bhi nahi milega, aur agar koi LLM call nahi hua toh footprint ka calculation bhi karke bekar
            # awaiting turn mein gate ka function_response + hamara message
            # kisi LLM call ko nahi gaye, wo E_tail hai
            tail = turn_contents[-2:] if status == "awaiting_confirmation" else []
            footprint_tokens, footprint_source = compute_footprint(
                calls=llm_calls,
                user_text=model_input,   # speech text nahi, jo history mein gaya wo
                tail_contents=tail,
                turn_contents=turn_contents,
            )    
        # failed turn state mein kabhi nahi jaata, purana del hack ab zaroori nahi    
        state.commit_turn(turn_index, turn_contents, footprint_tokens, status)
        save_turn(
            TurnRecord( # database is storing following values, mongodb, collection name "turns"
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
            llm_calls=llm_calls,
            usage_totals=usage_totals,
            footprint_tokens=footprint_tokens,
            footprint_source=footprint_source,
            failure_reason=failure_reason,
            )
        )

        if status =="failed": 
            continue                
        final_content = assistant_message or ""
        if not final_content:
            continue
        print("🗣️ LLM:", final_content)
        tts_result = tts.generate_tts(final_content=final_content)
        if not tts_result.success:
            print(f"TTS error: {tts_result.error}")
            continue

        audio_file = audio.create_temp_wav(pcm=tts_result.audio_data)
        try:
            audio.play_audio(audio_file)
        finally:
            audio_file.unlink(missing_ok=True) # whether the temporary file is played or not, delete it
           
