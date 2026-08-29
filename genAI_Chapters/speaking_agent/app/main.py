from core.logging_config import configure_logging
from workflow.chat_loop import run_conversation


def main() -> None:
    configure_logging()
    run_conversation()


if __name__ == "__main__":
    main()