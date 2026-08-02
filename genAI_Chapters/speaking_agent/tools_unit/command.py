import subprocess
from config import WORKING_DIRECTORY
def execute_command(command: str, timeout: int = 120):
    try:
        result = subprocess.run(
            command,
            shell=True,# ye chiz python ku bolti ki system ke native command shell me function chalao.
            capture_output=True, # It redirects and intercepts both the standard output (stdout) and standard error (stderr) of the running process,
            # stopping it from printing to the screen.
            text=True, #  It tells Python to automatically decode the incoming raw bytes(pc ki basha) from the operating system into a clean Python string 
            timeout=timeout,
            cwd=WORKING_DIRECTORY
        )
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] Command exceeded {timeout}s and was killed. It may be a long-running/blocking process (e.g. a dev server) — consider running it in the background instead."
    if result.returncode != 0:
        return f"[EXIT CODE {result.returncode}]\n{result.stderr.strip()}"
    return result.stdout.strip()