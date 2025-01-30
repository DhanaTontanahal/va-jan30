from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from core.config import CHUNK_SIZE, CHUNK_OVERLAP

def process_pdf(pdf_file):
    """Extract text from PDF and split into chunks."""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    text_splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    texts = text_splitter.split_text(text)
    
    return texts

def create_embeddings_and_vectorstore(texts):
    """Create embeddings and vector store from text chunks."""
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts, embeddings)
    return vectorstore

import fitz  # pymupdf
import io
from PIL import Image
import os

def extract_images_from_pdf(pdf_path, output_folder="static/extracted_images"):
    """
    Extracts images from a PDF file and saves them as PNG files.
    """
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
        for img_index, img in enumerate(doc[page_num].get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            img_ext = base_image["ext"]  # Image extension (png, jpeg, etc.)

            # Save image file
            img_path = os.path.join(output_folder, f"page_{page_num+1}_img_{img_index+1}.{img_ext}")
            with open(img_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            image_paths.append(img_path)

    return image_paths
