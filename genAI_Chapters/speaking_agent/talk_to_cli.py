from dotenv import load_dotenv
load_dotenv()
import subprocess
import requests
from pydantic import BaseModel,ValidationError
import speech_recognition  as sr
import simpleaudio as sa
recorgnize = sr.Recognizer()
from google import genai
from google.genai import types
import wave 
import base64 
import traceback
client = genai.Client()

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
- Working directory: C:\\Users\\moham\\Downloads\\Development\\GenerativeAI\\genAi_Chapters\\speaking_agent
  This is fixed as the tool's cwd for every call — you do not need to `cd` into it, and `cd`-ing within a single call will not persist to the next call since each execute_command runs as a fresh process. If you need to work in a subdirectory, prefix the specific command for that call (e.g. `cd subfolder; python script.py` as one PowerShell statement using `;` to chain), or use full/relative paths directly.
- Do not include a "PS C:\\...>" style prompt prefix in the commands you construct — that is just what the terminal displays, not something you type.

## Core Operating Principles
1. **Think before you act.** Before calling execute_command, briefly state (in 1-3 sentences) what you're about to do and why. Don't narrate excessively — one line of intent per command is enough.
2. **One command, one purpose.** Prefer small, verifiable steps over long chained commands. PowerShell chains with `;` (not `&&` unless the user's PowerShell version supports it — assume it doesn't unless verified). If a step fails, you want to know exactly which one failed.
3. **Read before you write.** Before editing or deleting a file, inspect it first (`Get-Content`, `Get-ChildItem`, `git status`) so you understand the current state. Never assume a file's contents or a directory's structure — verify.
4. **Verify after you act.** After a state-changing command (file edit, install, git operation, build), run a follow-up command to confirm it worked as intended, rather than assuming success from the absence of an error.
5. **Respect the timeout.** Commands are killed after `timeout` seconds (default 120). If a command is expected to be long-running or blocking by nature (dev servers, `npm start`, watch scripts), do not run it in the foreground expecting it to return — flag this to the user and ask how they want it handled (e.g. run detached, or ask user to run it themselves in a separate terminal).

When generating source code:
- Produce clean, human-readable code.
- Use proper indentation (4 spaces for Python, standard formatting for HTML/CSS/JS).
- Use line breaks appropriately.
- Never compress an entire file into a single line.
- Follow the language's common style conventions.
- The generated files should be production-quality and easy for humans to edit.

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
    types.Tool(
        function_declarations=[
            # 1. Weather Tool
            types.FunctionDeclaration(
                name="weather",
                description="Get current weather of a city",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "city": types.Schema(
                            type=types.Type.STRING,
                            description="City name"
                        )
                    },
                    required=["city"]
                )
            ),
            # 2. Execute Command Tool
            types.FunctionDeclaration(
                name="execute_command",
                description="Execute a shell command on the local machine and return the output.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "command": types.Schema(
                            type=types.Type.STRING,
                            description="The shell command to execute."
                        )
                    },
                    required=["command"]
                )
            )
        ]
    )
]
history: list[types.Content] = []
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2): # node for tts
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm) 
def play_audio(filename: str):
    subprocess.run(
        ["powershell", "-c",
         f"(New-Object Media.SoundPlayer '{filename}').PlaySync()"],
        check=True
    )
class weatherArgs(BaseModel):
    city : str
class commandArgs(BaseModel):
    command : str    
def weather(city:str) -> str:
    url = f"https://wttr.in/{city}?format=3"
    try : 
        response = requests.get(url,timeout=10)
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
            cwd=r"C:\Users\moham\Downloads\Development\GenerativeAI\genAi_Chapters\speaking_agent"
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
    with sr.Microphone() as mic:
        recorgnize.adjust_for_ambient_noise(mic) # clarity ke liye mic ku background noise se bachaye
        recorgnize.pause_threshold = 2 # here this wait for two seconds to accumulate audio
    try : # don know where this shit get crash silently, big problem big try-catch    
        while True:
            with sr.Microphone() as mic : # mic file is open
                    print("[🎙️]Speak")
                    audio = recorgnize.listen(mic) # actual record jahan mic open hai
                    print("Processing...")
                    try: # unknown input exception block
                        print("making speech to text for LLM")
                        user_audio_to_text = recorgnize.recognize_google(audio) # this particular call make text from speech so that i can give it to llm
                    except sr.UnknownValueError:
                        print("Samajh nahi aaya, phir bol...")
                        continue
                    except sr.RequestError as e: 
                        print(f"Speech API error: {e}")
                        continue
                    print("User:", user_audio_to_text)
            if user_audio_to_text.lower().strip() in ["exit", "band hojao","bye"]:
                print("Irshard V2: Acha waqt bacha raha toh phir milinge")
                break
            history.append( # apending or storing context in list typed dict, here our query is being stored
                        types.Content(
                            role="user", 
                                parts=[
                                    types.Part(text=user_audio_to_text) 
                                ]
                        )
                    )
            print("query registered in history")
            try: 
                response = client.models.generate_content(
                model="gemini-3.6-flash",  # Gemini me generate_content ke liye sahi model use karein
                    contents=history,          # OpenAI ke 'messages' ki jagah 'contents' use hota hai
                    config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,    
                    tools=tools            # Tools ko config ke andar pass kiya jata hai
                    )
                )       
            except Exception as ew:
                print(ew)
                traceback.print_exc()
                history.pop() # agar exception aaya response banate waqt to req jo append kare udadoh
                continue
            

                    # Pehle message ko handle karne ke liye (Loop start hone se pehle ka response)
                    # Agar aapke paas initial response hai, toh uski function_calls check karein
            function_calls = response.function_calls
            tool_call_count = 0
            while function_calls:
                tool_call_count += 1
                if tool_call_count > 5:
                    break
                # 1. Assistant ka function call response history me add karein (Gemini automatically requires the original function_call parts in history)
                # Note: Agar initial response directly models.generate_content se aaya hai, 
                # toh response.candidates[0].content ko aap seedhe history me append kar sakte hain.
                history.append(response.candidates[0].content)
                
                # Tool responses ko store karne ke liye list
                tool_response_parts = []
                
                # 2. Saare function calls ko execute karein
                for tool_call in function_calls:
                    function_name = tool_call.name
                    tool_info = TOOL_MAP.get(function_name)
                    if tool_info is None:
                        break
                    
                    # Gemini arguments directly dict (Python object) hote hain, json string nahi
                    try:
                        arguments = tool_info["schema"].model_validate(tool_call.args)
                    except ValidationError as e:
                        print(f"Validation failed: {e}")
                            # Yahan apna error handling code likhein (e.g., return, log, ya default values)
                        arguments = None
                        traceback.print_exc()
                    try:
                        result = tool_info["function"](**arguments.model_dump())
                    except Exception as e:
                        result = str(e)
                        traceback.print_exc()
                    
                    
                    # Gemini format me function ka result part banayein
                    # result ko string ya dict format me pass karein
                    tool_response_parts.append(
                        types.Part.from_function_response(
                            name=function_name,
                            response={"result": str(result)}  
                        )
                    )
                
                # 3. Tool ke saare results ko 'user' role ke saath history me append karein
                history.append(
                    types.Content(
                        role="user",
                        parts=tool_response_parts
                    )
                )
                
                # 4. Agla tool execution ya final reply lene ke liye model ko dobara call karein
                try:
                    print("[function unit] final response creation")
                    response = client.models.generate_content(
                        model="gemini-3.6-flash", # Sahi stable model identifier use karein
                        contents=history,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            tools=tools
                        )
                    )
                    # Agle loop ke liye check karein ki kya model fir se tool call karna chahta hai
                    function_calls = response.function_calls
                    
                except Exception as ew:
                    print(ew)
                    traceback.print_exc()
                    break
            try :            
            # Loop ke bahar, final text result print karein
                final_content = response.text or ""
            except Exception as e :
                traceback.print_exc()
            try: # speech client exception handling
                print("creating audio through ai response")
                interaction = client.interactions.create(
                model="gemini-3.1-flash-tts-preview",
                input=f"Speak naturally and conversationally: {final_content}", # defining style and input in input feild as google specifies
                response_format={"type": "audio"}, # response type declare
                generation_config={"speech_config": [{"voice": "Leda"}]} # speaker type 
                ) 
                print("ai audio created")
            except Exception as e:
                print(f"TTS error: {e}")
                traceback.print_exc()
                continue
            print("🗣️LLM:", final_content)
            print("playing ai audio")
            wave_file('out.wav', base64.b64decode(interaction.output_audio.data)) # audio speaking - which is made at line 277
            try:
                play_audio('out.wav')
            except Exception as e:
                print(f"Playback error: {e}")
                traceback.print_exc()
            # Final model response ko history me save karein
            print("llm response appended")
            if response.candidates and response.candidates[0].content:
                history.append(response.candidates[0].content)
            print("Loop completed peacefully ")            
    except Exception as e : # mega try catch
        traceback.print_exc()        
        

                       
if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        input("Press Enter...")       