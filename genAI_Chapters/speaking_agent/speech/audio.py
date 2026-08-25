import wave 
from pathlib import Path
import tempfile
import subprocess
def write_wav(
    filename: Path,
    pcm: bytes,
    channels: int = 1, #pre-defined
    rate: int = 24000, #pre-defined
    sample_width: int = 2, #pre-defined
) -> Path:

    with wave.open(str(filename), "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(rate)
        wav_file.writeframes(pcm)

    return filename
def create_temp_wav(pcm: bytes) -> Path:
    temp_file = tempfile.NamedTemporaryFile( # creating a temorary file in system
        suffix=".wav", 
        delete=False, # isse jab temporary file jab close hoti toh memory se delete nahi hoti
    )

    path = Path(temp_file.name) #temp_file jo ek temporary file hai uska file path dale in "path"

    temp_file.close() # temporary file off but not deleted

    return write_wav(
        filename=path,
        pcm=pcm,
    )
def play_audio(filename: Path) -> None: 
    audio_file = filename.resolve()

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