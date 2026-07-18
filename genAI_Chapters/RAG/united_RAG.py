from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
import os
from openai import OpenAI
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
doc_store = QdrantVectorStore.from_existing_collection( # ye woh bahar nikalra jo file- embed_with_langchain.py me dale at line 26
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name= "Ghayaz_irshard_basharat"
)

user_query = input("Ask To Find: ")
similar_result = doc_store.similarity_search(query=user_query)

context = []

context = "\n\n\n".join(
        [
            f"page Content: {result.page_content}\n"
            f"Page Number: {result.metadata["page_label"]}\n"
            f"Page Location: {result.metadata["source"]}"
            for result in similar_result
            ]
        )
SYSTEM_PROMPT = f"""
You are a retrieval-based question answering assistant.
Answer the user's question using only the provided context below.
Instructions:
- Carefully examine all provided context chunks before answering.
- If the answer can be inferred from the provided context, answer clearly.
- Cite the relevant page number(s) at the end of your response.
- If the answer genuinely cannot be found or inferred from the context, say:
  "Data for the proposed query is not present."
- Do not cite a page number if the answer is not present in the context.
Context:
{context}
"""
response = client.chat.completions.create(
                model="gemini-3.1-flash-lite",
                messages = [
                    {
                        "role" : "system",
                        "content" : SYSTEM_PROMPT
                    },
                    {
                        "role" : "user",
                        "content": user_query
                    }
                ]
)    
print(f"Irshard: {response.choices[0].message.content}")
    