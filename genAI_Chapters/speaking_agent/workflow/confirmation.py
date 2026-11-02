def is_confirmation(text: str) -> bool:
    return text.lower().strip() in {
        "yes",
        "y",
        "haan",
        "ha",
        "run it",
        "yes please", 
        "go ahead",
        "do it"
    }
def is_rejection(text: str) -> bool:
    return text.lower().strip() in {
        "no",
        "n",
        "nahi",
        "cancel",
        "stop",
    }        