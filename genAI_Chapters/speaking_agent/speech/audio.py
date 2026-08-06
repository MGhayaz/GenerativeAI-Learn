import wave 
from pathlib import Path
import subprocess
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2): # node for tts
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm) 
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