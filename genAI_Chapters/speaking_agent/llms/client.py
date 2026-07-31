from google import genai
def get_genai_client():
    client = genai.Client()
    return client