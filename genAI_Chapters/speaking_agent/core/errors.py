class ApplicationError(Exception):
    """Base exception for application-level failures."""


class LLMError(ApplicationError):
    """Raised when the LLM service fails."""


class SpeechError(ApplicationError):
    """Raised when speech infrastructure fails."""


class AudioError(ApplicationError):
    """Raised when audio processing or playback fails."""