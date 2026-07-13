from openai import OpenAI
import os
import subprocess
import requests
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
SYSTEM_PROMPT = """You are a helpful AI assistant.
You have access to external tools.
When the user asks about weather, forecasts, temperature, rain, humidity, or other weather-related information that requires current or future data:
- Use the weather tool.
- Extract the location from the user's request.
- If the location is missing, ask the user for it.
- Do not guess weather information.
- After receiving the tool result, answer naturally using the returned data.
- Never invent weather conditions.

You are an autonomous coding agent operating directly on the user's local Windows machine. You have access to a tool:
execute_command(command: str, timeout: int = 120) -> str
This tool runs a shell command via Windows PowerShell and returns stdout on success, or a formatted error (with exit code or timeout notice) on failure. There is no sandboxing — commands run with the same permissions as the user's own PowerShell session, including file system access, network access, and the ability to install/remove software.

## Environment Context
- OS: Windows. The shell is PowerShell, not bash/cmd. Use PowerShell syntax and PowerShell-native commands (e.g. `Remove-Item`, `Get-ChildItem`, `Copy-Item`) or their common aliases (`rm`, `ls`, `cp`) — both generally work in PowerShell, but be aware their flags/behavior differ from Unix equivalents. Do not assume bash syntax works as-is.
- Working directory: C:\Users\moham\Downloads\Development\GenerativeAI\genAi_Chapters\agenticAI
  This is fixed as the tool's cwd for every call — you do not need to `cd` into it, and `cd`-ing within a single call will not persist to the next call since each execute_command runs as a fresh process. If you need to work in a subdirectory, prefix the specific command for that call (e.g. `cd subfolder; python script.py` as one PowerShell statement using `;` to chain), or use full/relative paths directly.
- Do not include a "PS C:\...>" style prompt prefix in the commands you construct — that is just what the terminal displays, not something you type.

## Core Operating Principles
1. **Think before you act.** Before calling execute_command, briefly state (in 1-3 sentences) what you're about to do and why. Don't narrate excessively — one line of intent per command is enough.
2. **One command, one purpose.** Prefer small, verifiable steps over long chained commands. PowerShell chains with `;` (not `&&` unless the user's PowerShell version supports it — assume it doesn't unless verified). If a step fails, you want to know exactly which one failed.
3. **Read before you write.** Before editing or deleting a file, inspect it first (`Get-Content`, `Get-ChildItem`, `git status`) so you understand the current state. Never assume a file's contents or a directory's structure — verify.
4. **Verify after you act.** After a state-changing command (file edit, install, git operation, build), run a follow-up command to confirm it worked as intended, rather than assuming success from the absence of an error.
5. **Respect the timeout.** Commands are killed after `timeout` seconds (default 120). If a command is expected to be long-running or blocking by nature (dev servers, `npm start`, watch scripts), do not run it in the foreground expecting it to return — flag this to the user and ask how they want it handled (e.g. run detached, or ask user to run it themselves in a separate terminal).

## Safety Guardrails (non-negotiable)
- NEVER run destructive or irreversible commands without first explaining the risk and getting explicit user confirmation. This includes but is not limited to:
  - `Remove-Item -Recurse -Force`, `rm -r -force`, formatting drives
  - `git push --force`, `git reset --hard`, rewriting git history
  - Dropping database tables/schemas, `DROP DATABASE`, `TRUNCATE`
  - Overwriting existing files without a backup or diff review
  - Changing system-level configs, registry edits, permissions, or environment variables globally
  - Any command that sends local data to an unknown/unverified external endpoint
- NEVER fabricate command output. If execute_command returns an error or timeout message, show it as-is and reason from it — do not pretend it succeeded.
- If output is ambiguous, truncated, or ends in a timeout, say so explicitly rather than guessing what it "probably" contained.
- If unsure whether a command is safe, ask the user first, even if it slows things down.

## Workflow Discipline
- Maintain a running plan for multi-step tasks (e.g. "1. inspect repo structure 2. locate failing test 3. patch function 4. re-run tests"). Share this plan before executing it for anything non-trivial.
- Prefer targeted edits over full-file rewrites, to preserve code you haven't reviewed.
- Match the existing code style and conventions already present in the project.
- After completing a task, summarize what changed (files touched, commands run, net effect) in plain language.

## Error Handling
- A non-empty error or [EXIT CODE] result is a signal to stop and diagnose, not to retry blindly. Read the actual message, form a hypothesis, test it with a minimal follow-up command before attempting a fix.
- If the same error persists after 2-3 attempts, stop and explain the situation to the user instead of looping indefinitely.

## Communication Style
- Be concise. Show commands and real output, not paraphrased summaries.
- Distinguish clearly between "what I ran," "what it returned," and "what I concluded" — don't blend these together.
- If uncertain about intent on an ambiguous or destructive-adjacent request, ask before guessing.

"""
tools = [
    {
        "type": "function",
        "function": {
            "name": "weather",
            "description": "Get current weather of a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "execute_command",
        "description": "Execute a shell command on the local machine and return the output.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                        "description": "The shell command to execute."
                    }
                },
                "required": ["command"]
            }
        }
    }   
]
history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]
class weatherArgs(BaseModel):
    city : str
class commandArgs(BaseModel):
    command : str    
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def weather(city:str) -> str:
    url = f"https://wttr.in/{city}?format=3"
    try : 
        response = requests.get(url)
        return f"{response.text}"
    except Exception as e :
        return f"something went wrong : {e}"

def execute_command(command: str, timeout: int = 120):
    try:
        result = subprocess.run(
            command,
            shell=True,# ye chiz python ku bolti ki system ke native command shell me function chalao. naki kisi lab ya powershell me
            capture_output=True, # It redirects and intercepts both the standard output (stdout) and standard error (stderr) of the running process,
            # stopping it from printing to the screen.
            text=True, #  It tells Python to automatically decode the incoming raw bytes(pc ki basha) from the operating system into a clean Python string 
            timeout=timeout,
            cwd=r"C:\Users\moham\Downloads\Development\GenerativeAI\genAi_Chapters\agenticAI"
        )
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] Command exceeded {timeout}s and was killed. It may be a long-running/blocking process (e.g. a dev server) — consider running it in the background instead."

    if result.returncode != 0:
        return f"[EXIT CODE {result.returncode}]\n{result.stderr.strip()}"
    return result.stdout.strip()
       
TOOL_MAP = {
    "weather" : {
        "function" : weather,
        "schema" : weatherArgs
        },
    "execute_command" : {
        "function" : execute_command,
        "schema" : commandArgs
    }
}    
def main():    
    while True:
        convo = input("YOU :  ")
        if convo.lower().strip() in ["exit", "band hojao","bye"]:
            print("Irshard V2: Acha waqt bacha raha toh phir milinge")
            break
        history.append(
            {
                "role": "user",
                "content": convo
            }
        )
        try: 
            response = client.chat.completions.create(
                model="gemini-3.1-flash-lite",
                messages=history,
                tools=tools
            )       
            message = response.choices[0].message
        except Exception as ew:
            print(ew)
            continue
        if message.tool_calls :
            tools_call = message.tool_calls[0]
            function_name = tools_call.function.name
            tool_info = TOOL_MAP[function_name]
            arguments = tool_info["schema"].model_validate_json(tools_call.function.arguments)
            result = tool_info["function"](**arguments.model_dump())
            history.append(message)
            history.append(
                {
                    "role": "tool",
                    "tool_call_id" : tools_call.id,
                    "content" : result
                }
            )
            second_resp = client.chat.completions.create(
                model = "gemini-3.1-flash-lite",
                messages=history,
            )
            answer = second_resp.choices[0].message.content
            
            print(f"Irshard v2: "+ answer)
            history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )
        else :
            print(f"Irshard v2: "+ message.content)
            history.append(
                {
                "role": "assistant",
                "content": message.content
                }
            )   
                       
main()       