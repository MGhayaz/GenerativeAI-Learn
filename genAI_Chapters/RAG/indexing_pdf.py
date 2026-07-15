from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

pdf_path = Path(__file__).parent / "test_piece.pdf"

pdfload = PyPDFLoader(file_path=pdf_path)
doc = pdfload.load()

print(doc[3])


