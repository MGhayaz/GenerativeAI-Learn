from google.genai import types

from llms.context import ConversationState, ContextParams ,build_context , compact_content


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

# ---------- 3b.2: window + budget ----------

def plain_turn(i: int) -> list[types.Content]:
    return [user_text(f"q{i}"), model_text(f"a{i}")]


def state_with(footprints: list[int]) -> ConversationState:
    state = ConversationState(conversation_id="conv_test")
    for i, footprint in enumerate(footprints, start=1):
        state.commit_turn(i, plain_turn(i), footprint, "success")
    return state


def make_params(**overrides) -> ContextParams:
    base = dict(
        input_budget_tokens=1000,
        fixed_overhead_tokens=0,
        tool_reserve_tokens=0,
        low_ratio=0.5,
        keep_full_turns=2,
        min_recent_turns=2,
    )
    base.update(overrides)
    return ContextParams(**base)


def big_tool_turn(i: int) -> list[types.Content]:
    return [
        user_text(f"q{i}"),
        model_call("execute_command", {"command": "dir"}),
        tool_response("execute_command", "x" * 1000),
        model_text("done"),
    ]


def test_no_trim_below_high():
    built = build_context(state_with([100, 100, 100]), "", make_params())
    assert built.window_start == 0
    assert built.turns_included == 3
    assert built.info.trimmed_this_turn is False


def test_trim_drops_oldest_down_to_low():
    # HIGH=2000, LOW=1000. 2400 > HIGH, toh 2400 -> 800 tak (4 turns drop)
    built = build_context(state_with([400] * 6), "", make_params(input_budget_tokens=2000))
    assert built.window_start == 4
    assert built.turns_included == 2
    assert built.info.trimmed_this_turn is True
    assert built.info.turns_dropped_total == 4
    assert built.info.window_start_turn_index == 5
    assert built.contents[0].parts[0].text == "q5"


def test_min_recent_turns_respected():
    # budget se bade turns hain, par last 2 kabhi drop nahi hote
    built = build_context(state_with([900, 900, 900]), "", make_params())
    assert built.window_start == 1
    assert built.turns_included == 2


def test_single_turn_bigger_than_budget_is_kept():
    built = build_context(state_with([5000]), "", make_params())
    assert built.window_start == 0
    assert built.turns_included == 1
    assert len(built.contents) == 2


def test_window_start_persisted_gives_hysteresis():
    params = make_params(input_budget_tokens=2000)
    state = state_with([400] * 6)
    state.window_start = build_context(state, "", params).window_start
    assert state.window_start == 4

    for i in (7, 8, 9):  # total 2000, HIGH ke barabar, trim nahi
        state.commit_turn(i, plain_turn(i), 400, "success")
    quiet = build_context(state, "", params)
    assert quiet.info.trimmed_this_turn is False
    assert quiet.window_start == 4

    state.commit_turn(10, plain_turn(10), 400, "success")  # 2400 > HIGH, ek saath trim
    trimmed = build_context(state, "", params)
    assert trimmed.info.trimmed_this_turn is True
    assert trimmed.window_start == 8


def test_budget_math_uses_overhead_user_and_reserve():
    params = make_params(
        fixed_overhead_tokens=600,
        tool_reserve_tokens=200,
    )
    built = build_context(state_with([100]), "x" * 70, params)  # user_est = 20
    assert built.info.history_high == 180   # 1000 - 600 - 20 - 200
    assert built.info.history_low == 90
    assert built.info.fixed_overhead_tokens == 600
    assert built.info.predicted_prompt_tokens == 720   # 600 + 100 + 20


def test_old_tool_outputs_compacted_recent_kept_full():
    state = ConversationState(conversation_id="conv_test")
    for i in (1, 2, 3):
        state.commit_turn(i, big_tool_turn(i), 500, "success")

    built = build_context(
        state, "", make_params(input_budget_tokens=100_000, keep_full_turns=1)
    )
    results = [
        c.parts[0].function_response.response["result"]
        for c in built.contents
        if c.parts[0].function_response
    ]
    assert len(results) == 3
    assert len(results[0]) < 1000 and len(results[1]) < 1000
    assert len(results[2]) == 1000
    assert built.info.turns_compacted == 2
    assert built.info.chars_saved_by_compaction == 2 * (1000 - len(results[0]))
    # F7: effective footprint = 500 - int(677 / 3.5) = 307 (do turns), 500 (recent)
    assert built.info.predicted_prompt_tokens == 307 * 2 + 500


def test_build_context_does_not_mutate_state():
    state = ConversationState(conversation_id="conv_test")
    for i in (1, 2, 3):
        state.commit_turn(i, big_tool_turn(i), 500, "success")
    build_context(state, "", make_params(input_budget_tokens=100_000, keep_full_turns=1))
    original = state.turns[0].contents[2].parts[0].function_response.response["result"]
    assert original == "x" * 1000
    assert state.window_start == 0


def test_missing_footprint_falls_back_to_estimate():
    state = ConversationState(conversation_id="conv_test")
    state.commit_turn(1, TOOL_TURN, None, "success")
    built = build_context(state, "hi", make_params())
    assert built.turns_included == 1
    assert built.info.predicted_prompt_tokens > 0


def test_trimmed_context_keeps_invariants():
    # budget chhota, par awaiting turn (function_call + response pair) min_recent ki wajah se bacha
    built = build_context(make_state(), "", make_params(input_budget_tokens=400))
    assert built.window_start == 1
    assert built.turns_included == 2
    first = built.contents[0]
    assert first.role == "user" and first.parts[0].text == "delete the empty folder"
    for i, content in enumerate(built.contents):
        if any(p.function_call for p in content.parts):
            assert any(p.function_response for p in built.contents[i + 1].parts)


def test_same_input_same_output_with_params():
    state = make_state()
    params = make_params(input_budget_tokens=400)
    a = build_context(state, "hi", params)
    b = build_context(state, "hi", params)
    assert dump(a.contents) == dump(b.contents)
    assert a.info == b.info and a.window_start == b.window_start    