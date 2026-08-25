import wave 
from pathlib import Path
import subprocess
def write_wav(
    filename: Path,
    pcm: bytes,
    channels: int = 1,
    rate: int = 24000,
    sample_width: int = 2,
) -> Path:

    with wave.open(str(filename), "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(rate)
        wav_file.writeframes(pcm)

    return filename
def play_audio(filename: str) -> None: 
    audio_file = Path(filename).resolve()

    try:
        subprocess.run(
            [
                "powershell",
                "-Command",
                f"(New-Object Media.SoundPlayer '{audio_file}').PlaySync()"
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Audio playback failed:\n{e.stderr}"
        ) from e