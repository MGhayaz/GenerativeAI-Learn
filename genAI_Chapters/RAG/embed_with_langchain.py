from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
load_dotenv()
    
# pdf to text 
pdfpath = Path(__file__).parent / "test_piece.pdf"
pdfloader = PyPDFLoader(file_path=pdfpath)
doc = pdfloader.load()

# chunking/ text_split
text_spitter = RecursiveCharacterTextSplitter(
    chunk_size = 800, # ek chunk ka size 800 characters
    
    # ek chunk me sirf 800 new characters store nai karke, 
    # chunk_overlap me particular chunk ke previous chunk ka last 300 character bi store karta inorder to hold the context better, total size still 800 jisme 300 old, 500 new
    chunk_overlap = 300
)
chunks = text_spitter.split_documents(documents=doc) 

# embedding and Vector DB store in collectionRT
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview") # ek embedding model ku key ka use karke bulae
doc_store = QdrantVectorStore.from_documents( # doc_store banaya jisme chunks,model,vector db address aur collection name diye
    documents=chunks,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name= "Ghayaz_irshard_basharat"
)