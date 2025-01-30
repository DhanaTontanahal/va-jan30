import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
import asyncio
from pydantic import BaseModel
# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()

# Constants
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
MAX_OUTPUT_TOKENS = 4096
TEMPERATURE = 0.4
MODEL_NAME = "models/text-bison-001"  # Gemini model name
API_URL = "https://api.generativeai.google.com/v1beta2/models"

# Get OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

# Set Gemini API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in your .env file")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GEMINI_API_KEY}"
}

# FastAPI App
app = FastAPI()

# Load PDF from the project folder (knowledge base)
KNOWLEDGE_BASE_PDF = "knowledgebase.pdf"  # Replace with your PDF name


# Helper functions
def process_pdf(pdf_file):
    """Extract text from PDF and split into chunks."""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    text_splitter = CharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    texts = text_splitter.split_text(text)

    return texts


def create_embeddings_and_vectorstore(texts):
    """Create embeddings and vector store from text chunks."""
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectorstore = FAISS.from_texts(texts, embeddings)
    return vectorstore


def generate_text_with_gemini(prompt: str, max_tokens: int = MAX_OUTPUT_TOKENS) -> str:
    """Generate text using Gemini API."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "temperature": TEMPERATURE,
        "maxOutputTokens": max_tokens,
    }

    response = requests.post(f"{API_URL}/{MODEL_NAME}:generateText", headers=HEADERS, json=payload)

    if response.status_code != 200:
        raise Exception(f"Gemini API Error: {response.json()}")

    return response.json()["candidates"][0]["output"]


def expand_query(query: str) -> str:
    """Expand the original query with related terms using Gemini."""
    expand_prompt = f"""Given the following query, generate 3-5 related terms or phrases that could be relevant to the query. 
Separate the terms with commas.

Query: {query}

Related terms:"""

    response = generate_text_with_gemini(expand_prompt, max_tokens=50)
    expanded_terms = response.split(',')
    expanded_query = f"{query} {' '.join(term.strip() for term in expanded_terms)}"
    return expanded_query

def rag_pipeline_with_gemini(query, vectorstore):
    """Run the RAG pipeline using Gemini API."""
    expanded_query = expand_query(query)
    relevant_docs = vectorstore.similarity_search_with_score(expanded_query, k=3)

    context = "\n\n".join(doc.page_content for doc, _ in relevant_docs)

    final_prompt = f"""Context: {context}

Question: {query}

Answer the question concisely based on the given context. If the context doesn't contain relevant information, say 'I don’t have enough information to answer that question.'"""

    return generate_text_with_gemini(final_prompt)


# Process the knowledge base on startup
texts = process_pdf(KNOWLEDGE_BASE_PDF)
vectorstore = create_embeddings_and_vectorstore(texts)


async def streaming_response_generator(response):
    for line in response.splitlines():
        for char in line:
            yield char
            await asyncio.sleep(0.02)
        yield '\n'



# Define request schema
class QueryRequest(BaseModel):
    query: str


@app.post("/api/query")
async def query_api(request: QueryRequest):
    """Endpoint to handle queries."""
    try:
        # Extract query from the request body
        query = request.query
        answer = rag_pipeline_with_gemini(query, vectorstore)  # Process the query using RAG pipeline

        # Streaming response for "typing effect"
        async def streaming_response():
            for char in answer:
                yield char
                await asyncio.sleep(0.02)  # Simulate typing delay

        return StreamingResponse(streaming_response(), media_type="text/plain")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
