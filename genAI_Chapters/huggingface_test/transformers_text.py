from transformers import pipeline
# from transformers import AutoProcessor

# processor = AutoProcessor.from_pretrained(
#     "google/gemma-3-4b-it",
#     trust_remote_code=True
# )

# print(processor)
pipe = pipeline("image-text-to-text",model="google/gemma-3-4b-it")
messages=[
    {
        "role" : "user",
        "content" : [
            {"type": "image", "url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/p-blog/candy.JPG"},
                     {"type": "text", "text": "how many candies are of green/teal colour"}
            ]
    },
]
pipe(text=messages)
response = pipe(text=messages)

print(response)
