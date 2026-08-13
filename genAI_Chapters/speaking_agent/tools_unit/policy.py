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


def requires_confirmation(command: str) -> bool: # this method checks whether a danger causing word is present in user/commmand or query[taken as args]
    normalized_command = command.lower().strip()

    return any(
        pattern in normalized_command
        for pattern in DESTRUCTIVE_COMMAND_PATTERNS
    )