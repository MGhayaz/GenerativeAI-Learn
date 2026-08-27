from models.schemas import ToolDefinition
DESTRUCTIVE_COMMAND_PATTERNS = [ # list of words jisse scurtiny decide hoti
    "remove-item",
    "rm ",
    "rmdir",
    "del ",
    "format-",
    "clear-disk",
    "git reset --hard",
    "git push --force",
]

# not meant for security but for confirmation and check, this method allow chat loop to requestion[in voice] to user wheter danger-causing prompt is his explicit choice or not
def requires_confirmation(
    tool_definition: ToolDefinition,
    arguments: dict,
) -> bool:
    if not tool_definition.requires_confirmation:
        return False

    command = arguments.get("command", "")

    return is_destructive_command(command)

def is_destructive_command(command: str) -> bool:
    normalized_command = command.lower().strip()

    return any(
        pattern in normalized_command
        for pattern in DESTRUCTIVE_COMMAND_PATTERNS
    )