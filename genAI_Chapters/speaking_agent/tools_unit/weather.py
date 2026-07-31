import requests
def weather(city:str) -> str:
    url = f"https://wttr.in/{city}?format=3"
    try : 
        response = requests.get(url,timeout=10)
        return f"{response.text}"
    except Exception as e :
        return f"something went wrong : {e}"