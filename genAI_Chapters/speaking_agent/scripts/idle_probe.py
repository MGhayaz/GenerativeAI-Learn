"""Kya idle connection ke baad pehli call slow hoti hai?

Run: python -m scripts.idle_probe   (~3 min lagte hain)
"""


"""
Output kaise padhna hai (idle_probe Diagnostics):

1. idle_probe : Gap ke saath latency badhti hai (jaise 15s pe ~9s)
   App (abhi) : Slow
   Matlab     : Stale keep-alive connection
   Next       : Client ke HTTP options mein fix

2. idle_probe : Sab fast
   App (abhi) : Fast
   Matlab     : Us waqt API load tha
   Next       : Koi fix nahi, bas dhyan rakh

3. idle_probe : Sab fast
   App (abhi) : Slow
   Matlab     : App process mein kuch alag hai (audio libraries wagera)
   Next       : Probe mein speech_recognition import aur mic calibrate daal ke dobara test karenge

4. idle_probe : Sab slow
   App (abhi) : Slow
   Matlab     : Abhi API ya network slow hai
   Next       : Kuch ghante baad dobara
"""



import time

from google import genai
from google.genai import types

from core.config import settings
from prompts.system import SYSTEM_PROMPT
from tools.schema_builder import build_gemini_tools

GAPS_SECONDS = [0, 0, 15, 45, 90]
TEXT = "Say hi in one short sentence."


def main() -> None:
    client = genai.Client(api_key=settings.gemini_keys[0])  # ek hi connection pool
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=build_gemini_tools(),
        temperature=settings.model_temperature,
    )
    for gap in GAPS_SECONDS:
        time.sleep(gap) 
        started = time.perf_counter()
        client.models.generate_content(
            model=settings.model_name,
            contents=TEXT,
            config=config,
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        print(f"idle {gap:>3}s -> latency {latency_ms} ms")


if __name__ == "__main__":
    main()