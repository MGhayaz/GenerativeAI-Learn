from google.genai import types

from llms.context import state_from_docs
from tests.test_context import (
    AWAITING_TURN,
    PLAIN_TURN,
    TOOL_TURN,
    dump,
    model_text,
    user_text,
)


def doc(turn_index, contents, status="success", footprint=100):
    return {
        "conversation_id": "conv_test",
        "turn_index": turn_index,
        "status": status,
        "footprint_tokens": footprint,
        "llm_contents": dump(contents),
    }


def test_rebuilds_retained_turns_in_order():
    docs = [doc(4, PLAIN_TURN), doc(1, TOOL_TURN), doc(2, AWAITING_TURN, "awaiting_confirmation")]
    state = state_from_docs("conv_test", docs)  # ulta order mein diya
    assert [t.turn_index for t in state.turns] == [1, 2, 4]


def test_flatten_equals_original_contents():
    docs = [doc(1, TOOL_TURN), doc(2, AWAITING_TURN, "awaiting_confirmation"), doc(3, PLAIN_TURN)]
    state = state_from_docs("conv_test", docs)
    flat = [c for t in state.turns for c in t.contents]
    assert dump(flat) == dump(TOOL_TURN + AWAITING_TURN + PLAIN_TURN)


def test_failed_and_incomplete_turns_are_skipped():
    incomplete = [user_text("q"), types.Content(role="user", parts=[types.Part(text="x")])]
    docs = [doc(1, PLAIN_TURN), doc(2, [user_text("q")], "failed"), doc(3, incomplete)]
    state = state_from_docs("conv_test", docs)
    assert [t.turn_index for t in state.turns] == [1]


def test_footprint_and_status_are_carried():
    state = state_from_docs("conv_test", [doc(1, TOOL_TURN, "partial_failure", footprint=321)])
    assert state.turns[0].footprint_tokens == 321
    assert state.turns[0].status == "partial_failure"


def test_missing_footprint_stays_none():
    state = state_from_docs("conv_test", [doc(1, PLAIN_TURN, footprint=None)])
    assert state.turns[0].footprint_tokens is None


def test_corrupt_doc_is_skipped_not_fatal():
    bad = {
        "turn_index": 2,
        "status": "success",
        "llm_contents": [
            {"role": "user", "parts": [{"text": "hi"}]},
            {"role": "model", "parts": "not-a-list"},
        ],
    }
    state = state_from_docs("conv_test", [doc(1, PLAIN_TURN), bad])
    assert [t.turn_index for t in state.turns] == [1]


def test_empty_docs_give_empty_state():
    assert state_from_docs("conv_test", []).turns == []


def test_thought_signature_survives_db_roundtrip():
    content = types.Content(
        role="model", parts=[types.Part(text="ok", thought_signature=b"sig-bytes-123")]
    )
    state = state_from_docs("conv_test", [doc(1, [user_text("q"), content])])
    assert state.turns[0].contents[1].parts[0].thought_signature == b"sig-bytes-123"