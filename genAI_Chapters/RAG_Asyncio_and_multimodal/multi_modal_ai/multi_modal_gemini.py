from google import genai
from dotenv import load_dotenv
load_dotenv()
client = genai.Client()

# for public resp calls, use generate_content
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=[
        {
            "role": "user",
            "parts": [
                {"text": "Describe this image in hyderabadi style."},
                {
                    "file_data": {
                        "file_uri": "https://imgs.search.brave.com/I2XqC_vxRMd4VAuLubu1sy2AcCyqiLjWKD_FEYY-ldU/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pbWFn/ZXMuaW1tZWRpYXRl/LmNvLnVrL3Byb2R1/Y3Rpb24vdm9sYXRp/bGUvc2l0ZXMvMy8y/MDIxLzA5L2Rhbmll/bC1jcmFpZy0wMDcu/anBnLTMwM2E3MzAu/cG5nP3F1YWxpdHk9/OTAmcmVzaXplPTYy/MCw0MTQ",
                        "mime_type": "image/jpeg"
                    }
                }
            ]
        }
    ]
)

print(response.text)


# for local images use interactions
# uploaded_file = client.files.upload(file=r"C:\Users\moham\Downloads\IMG_20251125_111359.png")


# interaction = client.interactions.create(
#     model="gemini-3.5-flash",
#     input=[
#         {"type": "text", "text": "Caption this image."},
#         {
#             "type": "image",
#             "uri": uploaded_file.uri,
#             "mime_type": uploaded_file.mime_type
#         }
#     ]
# )
# print(interaction.output_text)