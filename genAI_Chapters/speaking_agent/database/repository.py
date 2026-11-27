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

def load_turns(conversation_id: str, limit: int = 50) -> list[dict]:
    """Conversation ke last `limit` turns (saare statuses), turn_index ascending."""
    try:
        docs = list(
            turns_collection.find({"conversation_id": conversation_id})
            .sort("turn_index", -1)
            .limit(limit)
        )
    except PyMongoError:
        logger.error("Failed to load turns", exc_info=True)
        return []
    docs.reverse()
    return docs


def latest_conversation_id() -> str | None:
    try:
        doc = turns_collection.find_one(
            {}, sort=[("created_at", -1)], projection={"conversation_id": 1}
        )
    except PyMongoError:
        logger.error("Failed to find latest conversation", exc_info=True)
        return None
    return doc["conversation_id"] if doc else None