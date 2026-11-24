from google.genai import types

from llms.context import ConversationState, build_context , compact_content


def user_text(text: str) -> types.Content:
    return types.Content(role="user", parts=[types.Part(text=text)])


def model_text(text: str) -> types.Content:
    return types.Content(role="model", parts=[types.Part(text=text)])


def model_call(name: str, args: dict) -> types.Content:
    return types.Content(
        role="model",
        parts=[types.Part(function_call=types.FunctionCall(name=name, args=args))],
    )


def tool_response(name: str, result: str) -> types.Content:
    return types.Content(
        role="user",
        parts=[
            types.Part.from_function_response(
                name=name, response={"success": True, "result": result}
            )
        ],
    )


TOOL_TURN = [
    user_text("weather in Vizag"),
    model_call("weather", {"city": "Vizag"}),
    tool_response("weather", "Vizag: +29C"),
    model_text("It is 29 degrees in Vizag."),
]
AWAITING_TURN = [
    user_text("delete the empty folder"),
    model_call("execute_command", {"command": "Remove-Item x"}),
    tool_response("execute_command", "confirmation required"),
    model_text("Final Call for: Remove-Item x. Say yes to proceed or no to cancel."),
]
FAILED_TURN = [user_text("what is up")]  # adhoora, response aaya hi nahi
PLAIN_TURN = [user_text("thanks"), model_text("Welcome.")]


def dump(contents: list[types.Content]) -> list[dict]:
    return [c.model_dump(mode="json", exclude_none=True) for c in contents]


def make_state() -> ConversationState:
    state = ConversationState(conversation_id="conv_test")
    state.commit_turn(1, TOOL_TURN, 300, "success")
    state.commit_turn(2, AWAITING_TURN, 180, "awaiting_confirmation")
    state.commit_turn(3, FAILED_TURN, None, "failed")
    state.commit_turn(4, PLAIN_TURN, 40, "success")
    return state


def test_empty_state():
    built = build_context(ConversationState(conversation_id="conv_test"))
    assert built.contents == []
    assert built.turns_included == 0


def test_flatten_matches_old_flat_history():
    # purana tareeka: failed hata ke sab contents ek flat list mein
    old_flat = TOOL_TURN + AWAITING_TURN + PLAIN_TURN
    assert dump(build_context(make_state()).contents) == dump(old_flat)


def test_failed_turn_not_retained():
    state = make_state()
    assert [t.turn_index for t in state.turns] == [1, 2, 4]
    assert state.commit_turn(5, FAILED_TURN, None, "failed") is False
    assert len(state.turns) == 3


def test_awaiting_turn_retained():
    state = make_state()
    awaiting = [t for t in state.turns if t.status == "awaiting_confirmation"]
    assert len(awaiting) == 1 and awaiting[0].turn_index == 2


def test_no_orphan_function_calls():
    out = build_context(make_state()).contents
    for i, content in enumerate(out):
        if any(p.function_call for p in content.parts):
            assert any(p.function_response for p in out[i + 1].parts)


def test_first_content_is_user_text():
    first = build_context(make_state()).contents[0]
    assert first.role == "user" and first.parts[0].text


def test_build_context_returns_a_copy():
    state = make_state()
    out = build_context(state).contents
    out.append(user_text("extra"))
    assert len(build_context(state).contents) == 10  # state par asar nahi


def test_commit_turn_copies_input_list():
    state = ConversationState(conversation_id="conv_test")
    current = list(PLAIN_TURN)
    state.commit_turn(1, current, 10, "success")
    current.append(user_text("later"))
    assert len(state.turns[0].contents) == 2


def test_same_input_same_output():
    state = make_state()
    assert dump(build_context(state).contents) == dump(build_context(state).contents)

def test_compact_trims_long_result():
    content = tool_response("execute_command", "x" * 1000)
    out, saved = compact_content(content, 300)
    result = out.parts[0].function_response.response["result"]
    assert result.startswith("x" * 300)
    assert "[trimmed 700 chars]" in result
    assert saved == 1000 - len(result)


def test_compact_leaves_short_result_untouched():
    content = tool_response("weather", "Vizag: +29C")
    out, saved = compact_content(content, 300)
    assert out is content and saved == 0


def test_compact_does_not_mutate_original():
    content = tool_response("execute_command", "x" * 1000)
    compact_content(content, 300)
    assert content.parts[0].function_response.response["result"] == "x" * 1000


def test_compact_never_touches_function_call_or_text():
    for content in (
        model_call("weather", {"city": "Vizag"}),
        model_text("y" * 1000),
        user_text("z" * 1000),
    ):
        out, saved = compact_content(content, 300)
        assert out is content and saved == 0


def test_compact_keeps_structure_and_other_fields():
    content = tool_response("execute_command", "x" * 1000)
    out, _ = compact_content(content, 300)
    part = out.parts[0].function_response
    assert part.name == "execute_command"
    assert part.response["success"] is True
    assert len(out.parts) == 1 and out.role == "user"


def test_compact_trims_error_field_too():
    content = types.Content(
        role="user",
        parts=[
            types.Part.from_function_response(
                name="execute_command",
                response={"success": False, "result": None, "error": "e" * 1000},
            )
        ],
    )
    out, saved = compact_content(content, 300)
    assert out.parts[0].function_response.response["error"].startswith("e" * 300)
    assert saved > 0


def test_compact_skips_when_stub_would_not_be_shorter():
    content = tool_response("execute_command", "x" * 310)  # stub ~322 chars, original se bada
    out, saved = compact_content(content, 300)
    assert out is content and saved == 0    