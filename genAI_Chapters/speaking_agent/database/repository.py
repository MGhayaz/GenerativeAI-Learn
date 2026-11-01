import logging
from pymongo.errors import PyMongoError
from database.mongodb_client import turns_collection
from models.schemas import TurnRecord

logger = logging.getLogger(__name__)
def save_turn(turn: TurnRecord) -> None:
    # DB failure must never kill the voice loop
    try:
        turns_collection.insert_one(turn.model_dump())
    except PyMongoError:
        logger.error("Failed to persist turn", exc_info=True)