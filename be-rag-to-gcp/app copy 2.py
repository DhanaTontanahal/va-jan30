from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from core.models import QueryRequest
from core.pipeline import rag_pipeline, streaming_response_generator
from core.utils import process_pdf, create_embeddings_and_vectorstore
import time

from fastapi.middleware.cors import CORSMiddleware



# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Process knowledge base at startup
KNOWLEDGE_BASE_PDF = "core/knowledgebase/knowledgebase.pdf"
texts = process_pdf(KNOWLEDGE_BASE_PDF)
vectorstore = create_embeddings_and_vectorstore(texts)

@app.post("/api/query")
async def query_api(request: QueryRequest):
    """Endpoint to handle queries."""
    start_time = time.time()
    try:
        query = request.query
        answer = rag_pipeline(query, vectorstore)
        elapsed_time = time.time() - start_time
        return JSONResponse(content={"query": query,"sender":"assistant", "answer": answer,"processing_time": f"{elapsed_time:.2f} seconds"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
