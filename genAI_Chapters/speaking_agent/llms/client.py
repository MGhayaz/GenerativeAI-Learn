from threading import Lock  
from google import genai 
from core.config import settings 

_index = 0  # Tracks which Gemini API key should be used next.
_lock = Lock()  # Creates a mutex to prevent multiple threads from modifying shared state simultaneously.
_clients: dict[str, genai.Client] = {}  # Stores initialized Gemini clients, mapped by their API keys.


def get_client() -> genai.Client: 
    global _index  # Allows this function to modify the global API key index.

    with _lock:  # Acquires the lock to make the following operations thread-safe.
        key = settings.gemini_keys[_index]  # Selects the current Gemini API key using the round-robin index.
        client = _clients.get(key)  # Checks whether a client for this API key already exists.

        if client is None:  # Checks whether the client has not been initialized yet.
            client = genai.Client(api_key=key)  # Creates a new Gemini client using the selected API key.
            _clients[key] = client  # Caches the client so it can be reused in future requests.

        _index = (_index + 1) % len(settings.gemini_keys)  # Advances to the next API key, wrapping around to the first key.
        return client  # Returns the selected Gemini client.