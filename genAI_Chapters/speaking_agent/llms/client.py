from threading import Lock

from google import genai
from core.config import settings

_index = 0
_lock = Lock()
_clients: dict[str, genai.Client] = {}


def get_client() -> genai.Client:
    global _index

    with _lock:
        key = settings.gemini_keys[_index]
        client = _clients.get(key)

        if client is None:
            client = genai.Client(api_key=key)
            _clients[key] = client

        _index = (_index + 1) % len(settings.gemini_keys)
        return client