import subprocess
from models.schemas import ToolResult
from config import WORKING_DIRECTORY
def execute_command(command: str, timeout: int = 120)-> ToolResult:
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
    except subprocess.TimeoutExpired: # zyada time liya toh exeption
        return ToolResult( success=False, error=( f"Command exceeded {timeout}s and was terminated."),)
    except OSError as e: # os me apna command nahi chala toh
        return ToolResult(
            success=False,
            error=f"Command execution failed: {e}",
        )
    if result.returncode != 0: # in build subprocess's function, it returns 0 if all is good, else return 1 or something
        return ToolResult(
            success=False,
            error=(
                f"[EXIT CODE {result.returncode}]\n"
                f"{result.stderr.strip()}"
            ),
        )
    # agar try chalgaya, and koi return code niyaya toh ye chal jata aur success return karta
    return ToolResult(
        success=True,
        result=result.stdout.strip(),
    )