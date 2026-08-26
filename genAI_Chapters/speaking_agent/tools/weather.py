import requests
from models.schemas import ToolResult  # success: bool, result: str | None = None, error: str | None = None 
def weather(city:str) -> str:
    url = f"https://wttr.in/{city}?format=3"
    try:
        response = requests.get(
            url,
            timeout=10,
        )
        response.raise_for_status() # HTTP 200 → success, HTTP 404/500 → exception , meant for fastAPI, 
        # inne agar success hua toh niche ka return chalata 
        # aur agar api tuti toh try block todta jahan inne hai aur exception block chaljata jisme error aur success false hai
        return ToolResult(
            success=True,
            result=response.text.strip(),
        )

    except requests.RequestException as e:
        return ToolResult(
            success=False,
            error=f"Weather request failed: {e}",
        )