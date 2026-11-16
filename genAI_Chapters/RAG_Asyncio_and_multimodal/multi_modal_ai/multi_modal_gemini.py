from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()
client = genai.Client()

# for public resp calls, use generate_content
# response = client.models.generate_content(
#     model="gemini-3.5-flash",
#     contents=[
#         {
#             "role": "user",
#             "parts": [
#                 {"text": "Describe this image as a hyderabadi who loves Vizag."},
#                 {
#                     "file_data": {
#                         "file_uri": "https://lh3.googleusercontent.com/gg/AJWXcNetj5SzAXhpdlubJsVVkxPVAmyYy3SPUdUe-ifWv18LwzYtb0y5z9wWIOwFi4VOmRJYE8OjiqvZrZK2krd1s9rl0eZ4G3Zo9CeMjYuHFqndPaNtUqYHKqLK46QTlTura2M0ix75_VNlwy7pJeG5KHFwchwgIRqxVPFsH0fQTLjU4rqw3fvxQiXkofO_625uT94b7NxYSNK7Novu49dZG-D5hu5Hk20etDyChPCclVZUCucc84HugJQQ2AfFBnqbp3xwHar1qFFg96-VEaO9qA1aLjpdNjriO2ZCEiFImqeVcEHls7vAibS5l_tfyZ4St5M53CXAEoQWTd0XJVJaTM4=s1600",
#                         "mime_type": "image/jpeg"
#                     }
#                 }
#             ]
#         }
#     ]
# )

# print(response.text)


# for local images use interactions
uploaded_file = client.files.upload(file=r"c:\Users\moham\Downloads\Gemini_Generated_Image.jpeg")


interaction = client.interactions.create(
    model="gemini-3.5-flash",
    input=[
        {"type": "text", "text": "Caption this image."},
        {
            "type": "image",
            "uri": uploaded_file.uri,
            "mime_type": uploaded_file.mime_type
        }
    ],
    generation_config={
        "max_output_tokens": 5000  # 100 ki jagah 500 rakhein taaki thinking tokens me response cut na ho
    },
)
print(interaction.output_text)