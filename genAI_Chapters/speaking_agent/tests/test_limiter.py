from tools.limiter import cap_text


def test_short_text_unchanged():
    result = cap_text('hello', 100)
    assert result.text == 'hello'
    assert result.truncated is False
    assert result.original_chars == 5


def test_exactly_at_limit_unchanged():
    text = 'x' * 100
    result = cap_text(text, 100)
    assert result.text == text and result.truncated is False


def test_long_text_keeps_head_and_tail():
    text = 'A' * 5000 + 'B' * 5000
    result = cap_text(text, 1000)
    assert result.truncated is True
    assert result.text.startswith('A' * 700)
    assert result.text.endswith('B' * 300)


def test_marker_reports_correct_omitted_count():
    result = cap_text('z' * 5000, 1000)
    assert '[... 4000 chars omitted ...]' in result.text


def test_original_chars_is_preserved():
    assert cap_text('z' * 5000, 1000).original_chars == 5000


def test_unicode_and_emoji_safe():
    text = '🌦️ +29°C ' * 1000
    result = cap_text(text, 500)
    assert result.truncated is True
    result.text.encode('utf-8')  # encode error nahi aana chahiye


def test_output_is_bounded():
    result = cap_text('x' * 100_000, 4000)
    assert len(result.text) < 4000 + 100  # limit + marker