import os
import re
from dataclasses import dataclass
from pathlib import Path

from models.schemas import PendingAction

MAX_PROBE_ENTRIES = 500
MAX_TARGETS = 3
MAX_COMMAND_PREVIEW = 300

# (regex, action, irreversible). Pehla match jeetta hai. Jo yahan nahi hai woh generic message pe jaata hai.
_ACTIONS: list[tuple[re.Pattern, str, bool]] = [
    (re.compile(r"\b(remove-item|rmdir|rm|rd|del|erase)\b", re.I), "delete", True),
    (re.compile(r"\b(move-item|mv)\b", re.I), "move", False),
    (re.compile(r"\b(rename-item|ren)\b", re.I), "rename", False),
    (re.compile(r"\b(set-content|out-file|clear-content)\b", re.I), "overwrite", True),
    (re.compile(r"\b(stop-process|taskkill|kill)\b", re.I), "stop", False),
]
_LEADING_CD = re.compile(
    r"^\s*(?:cd|set-location|sl)\s+(?:\"([^\"]+)\"|'([^']+)'|([^;\s]+))\s*;", re.I
)
_TOKEN = re.compile(r"\"([^\"]+)\"|'([^']+)'|([^\s,;|)}]+)")
_SEGMENT_END = re.compile(r"[;|}]")
_PATH_PARAMS = {"-path", "-literalpath"}


@dataclass(frozen=True)
class ConfirmationMessage:
    display: str  # terminal + history + DB: poori command ke saath
    spoken: str   # TTS: chhota, bina symbols


@dataclass(frozen=True)
class TargetInfo:
    path: Path
    kind: str            # 'folder' | 'file' | 'missing'
    files: int = 0
    folders: int = 0
    size_bytes: int = 0
    capped: bool = False  # MAX_PROBE_ENTRIES tak hi gine


def _base_dir(command: str, working_dir: Path) -> tuple[Path, str]:
    """Command ke shuru mein `cd X;` ho toh relative paths us X se resolve honge."""
    match = _LEADING_CD.match(command)
    if not match:
        return working_dir, command
    raw = next(group for group in match.groups() if group)
    return Path(raw), command[match.end():]


def _parse(command: str) -> tuple[str, bool, set[str], list[str]] | None:
    """-> (action, irreversible, flags, targets). Samajh na aaye toh None."""
    for pattern, action, irreversible in _ACTIONS:
        match = pattern.search(command)
        if not match:
            continue
        tail = command[match.end():]
        segment = _SEGMENT_END.split(tail, maxsplit=1)[0]
        flags: set[str] = set()
        targets: list[str] = []
        for quoted_d, quoted_s, bare in _TOKEN.findall(segment):
            value = quoted_d or quoted_s or bare
            if not (quoted_d or quoted_s) and value.startswith("-"):
                flags.add(value.lower())
                continue
            if value.lower() in _PATH_PARAMS:
                continue
            targets.append(value)
        return action, irreversible, flags, targets[:MAX_TARGETS + 1]
    return None


def probe_target(path: Path, limit: int = MAX_PROBE_ENTRIES) -> TargetInfo:
    """Sirf metadata dekhta hai: kuch padhta ya badalta nahi, symlinks follow nahi karta."""
    try:
        if not path.exists():
            return TargetInfo(path=path, kind="missing")
        if path.is_file():
            return TargetInfo(path=path, kind="file", size_bytes=path.stat().st_size)

        files = folders = size = 0
        stack = [path]
        while stack:
            with os.scandir(stack.pop()) as entries:
                for entry in entries:
                    if files + folders >= limit:
                        return TargetInfo(path, "folder", files, folders, size, capped=True)
                    if entry.is_symlink():
                        files += 1
                    elif entry.is_dir(follow_symlinks=False):
                        folders += 1
                        stack.append(Path(entry.path))
                    else:
                        files += 1
                        size += entry.stat(follow_symlinks=False).st_size
        return TargetInfo(path, "folder", files, folders, size)
    except OSError:
        return TargetInfo(path=path, kind="missing")


def _fmt_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def _plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def _contents_text(info: TargetInfo) -> str:
    if info.kind != "folder":
        return ""
    if info.files == 0 and info.folders == 0:
        return "empty"
    plus = "+" if info.capped else ""
    parts = []
    if info.files:
        parts.append(_plural(info.files, "file") if not plus else f"{info.files}+ files")
    if info.folders:
        parts.append(_plural(info.folders, "folder") if not plus else f"{info.folders}+ folders")
    return ", ".join(parts) + (f", {_fmt_size(info.size_bytes)}" if info.size_bytes else "")


def _generic(command: str) -> ConfirmationMessage:
    preview = command if len(command) <= MAX_COMMAND_PREVIEW else command[:MAX_COMMAND_PREVIEW] + "..."
    return ConfirmationMessage(
        display=(
            "This command can change files or settings on your machine.\n"
            f"Command: {preview}\n"
            "Say yes to proceed or no to cancel."
        ),
        spoken="I am about to run a command that can change your files. Say yes to proceed, or no to cancel.",
    )


def build_confirmation_message(action: PendingAction, working_dir: Path) -> ConfirmationMessage:
    command = str(action.arguments.get("command", "")).strip()
    parsed = _parse(command) if command else None
    if parsed is None or not parsed[3]:
        return _generic(command)

    verb, irreversible, flags, targets = parsed
    base, _ = _base_dir(command, working_dir)
    first = targets[0]
    has_wildcard = any(ch in first for ch in "*?$")
    path = Path(first) if Path(first).is_absolute() else base / first

    workspace = working_dir.resolve()
    try:
        resolved = path.resolve()
        outside = not resolved.is_relative_to(workspace)
        shown = resolved.relative_to(workspace).as_posix() if not outside else str(resolved)
    except (OSError, ValueError):
        return _generic(command)

    extra = len(targets) - 1
    more = f" and {extra} more" if extra > 0 else ""
    info = None if has_wildcard else probe_target(resolved)

    # kya hoga (display + spoken ke liye alag phrasing)
    if info is None:
        what, what_spoken, impact = f"'{shown}'{more}", f"items matching {first}", ""
    elif info.kind == "missing":
        what, what_spoken, impact = f"'{shown}'{more}", f"{resolved.name}", "not found, nothing will change"
    else:
        noun = "folder" if info.kind == "folder" else "file"
        impact = _contents_text(info)
        what = f"{noun} '{shown}'{more}"
        what_spoken = f"the {resolved.name} {noun}"

    recursive = bool(flags & {"-recurse", "-r", "-rf", "-fr"})
    inside = " and everything inside it" if (info and info.kind == "folder" and verb == "delete" and (recursive or info.files or info.folders)) else ""
    location = "outside your playground folder" if outside else "in playground"
    warning = "This cannot be undone." if irreversible else ""

    display_lines = [f"Confirm: {verb} {what} ({location})" + (f" [{impact}]" if impact else "") + inside + "."]
    if outside:
        display_lines.append("WARNING: this path is OUTSIDE the playground folder.")
    if warning:
        display_lines.append(warning)
    display_lines.append(f"Command: {command if len(command) <= MAX_COMMAND_PREVIEW else command[:MAX_COMMAND_PREVIEW] + '...'}")
    display_lines.append("Say yes to proceed or no to cancel.")

    spoken_bits = [f"I am about to {verb} {what_spoken}"]
    if info and info.kind == "folder" and (info.files or info.folders):
        spoken_bits[0] += f", with {_plural(info.files + info.folders, 'item')} inside"
    spoken_bits[0] += f", {location}."
    if outside:
        spoken_bits.append("Careful, this is not your playground.")
    if warning:
        spoken_bits.append("This can't be undone.")
    spoken_bits.append("Say yes to proceed, or no to cancel.")

    return ConfirmationMessage(display="\n".join(display_lines), spoken=" ".join(spoken_bits))