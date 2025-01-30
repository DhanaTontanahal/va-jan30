from fastapi import FastAPI
from fastapi.responses import JSONResponse
from core.models import QueryRequest
from core.pipeline import rag_pipeline
from core.utils import process_pdf, create_embeddings_and_vectorstore, extract_images_from_pdf
import time
import os

# Initialize FastAPI app
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# PDF File Path (Replace with your actual credit card PDF)
PDF_FILE_PATH = "core/knowledgebase/knowledgebase.pdf"

# Process knowledge base at startup
KNOWLEDGE_BASE_PDF = "core/knowledgebase/knowledgebase.pdf"
texts = process_pdf(KNOWLEDGE_BASE_PDF)
vectorstore = create_embeddings_and_vectorstore(texts)

@app.post("/api/query")
async def query_api(request: QueryRequest):
    """Endpoint to handle queries including image extraction."""
    start_time = time.time()
    query = request.query.lower()
    
    try:
        # Check if the query is about credit card images
        if "types of credit card" in query or "credit card design" in query:
            image_paths = extract_images_from_pdf(PDF_FILE_PATH)
            base_url = "http://127.0.0.1:8000/static/extracted_images/"
            image_urls = [base_url + os.path.basename(path) for path in image_paths]

            elapsed_time = time.time() - start_time
            return JSONResponse(content={
                "query": query,
                "images": image_urls,
                "answer": "Here are some famous credit card types offered by LLoyds banking group.",
                "processing_time": f"{elapsed_time:.2f} seconds"
            }, status_code=200)
        
        # Otherwise, process normal queries
        answer = rag_pipeline(query, vectorstore)
        elapsed_time = time.time() - start_time
        
        return JSONResponse(content={
            "query": query,
            "answer": answer,
            "processing_time": f"{elapsed_time:.2f} seconds"
        }, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Serve static images
#from fastapi.staticfiles import StaticFiles
#app.mount("/static", StaticFiles(directory="extracted_images"), name="static")

from fastapi.staticfiles import StaticFiles
import os


# Ensure extracted_images directory exists
EXTRACTED_IMAGES_DIR = "static/extracted_images"
os.makedirs(EXTRACTED_IMAGES_DIR, exist_ok=True)

# Mount static directory properly
app.mount("/static", StaticFiles(directory="static"), name="static")
