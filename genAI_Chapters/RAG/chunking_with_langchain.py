from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path

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



