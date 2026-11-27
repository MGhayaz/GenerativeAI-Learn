import argparse
from core.logging_config import configure_logging
from workflow.chat_loop import run_conversation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--resume",
        nargs="?",
        const="latest",
        default=None,
        help="--resume = latest conversation, --resume conv_xxx = specific",
    )
    args = parser.parse_args()
    configure_logging()
    run_conversation(resume=args.resume)


if __name__ == "__main__":
    main()