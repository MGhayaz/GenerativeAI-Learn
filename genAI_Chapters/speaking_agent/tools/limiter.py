from dataclasses import dataclass

HEAD_RATIO = 0.7


@dataclass(frozen=True)
class CappedText:
    text: str
    original_chars: int
    truncated: bool


def cap_text(text: str, max_chars: int) -> CappedText:
    """Text max_chars se bada ho toh head 70% + tail 30% rakho, beech mein marker."""
    original_chars = len(text)
    if original_chars <= max_chars:
        return CappedText(text=text, original_chars=original_chars, truncated=False)

    head_chars = int(max_chars * HEAD_RATIO)
    tail_chars = max_chars - head_chars
    omitted = original_chars - head_chars - tail_chars
    marker = f"\n[... {omitted} chars omitted ...]\n"

    tail = text[-tail_chars:] if tail_chars > 0 else ""
    return CappedText(
        text=text[:head_chars] + marker + tail,
        original_chars=original_chars,
        truncated=True,
    )