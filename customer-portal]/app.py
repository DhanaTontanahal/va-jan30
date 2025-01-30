import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import PromptTemplate
import fitz  # pymupdf
import pytesseract
from PIL import Image
import io
import asyncio
import pandas as pd

# Load environment variables
load_dotenv()

# Constants
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
MAX_TOKENS = 4096
MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.4

# Get OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

# Initialize LLM
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model_name=MODEL_NAME,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS
)

PROMPT = PromptTemplate(
    template="""Context: {context}

Question: {question}

Answer the question concisely based on the given context. If the context doesn't contain relevant information, say 'I don’t have enough information to answer that question.'""",
    input_variables=["context", "question"]
)


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
    
    text_splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    texts = text_splitter.split_text(text)
    
    return texts

def create_embeddings_and_vectorstore(texts):
    """Create embeddings and vector store from text chunks."""
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts, embeddings)
    return vectorstore

def expand_query(query: str, llm: ChatOpenAI) -> str:
    """Expand the original query with related terms."""
    prompt = PromptTemplate(
        input_variables=["query"],
        template="""Given the following query, generate 3-5 related terms or phrases that could be relevant to the query. 
        Separate the terms with commas.
        
        Query: {query}
        
        Related terms:"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(query)
    expanded_terms = [term.strip() for term in response.split(',')]
    expanded_query = f"{query} {' '.join(expanded_terms)}"
    return expanded_query

def rag_pipeline(query, vectorstore):
    """Run the RAG pipeline."""
    expanded_query = expand_query(query, llm)
    relevant_docs = vectorstore.similarity_search_with_score(expanded_query, k=3)
    
    context = ""
    for doc, score in relevant_docs:
        context += doc.page_content + "\n\n"

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    response = qa_chain.invoke({"query": query})
    return response['result']

# Process the knowledge base on startup
texts = process_pdf(KNOWLEDGE_BASE_PDF)
vectorstore = create_embeddings_and_vectorstore(texts)

# Streaming response generator
async def streaming_response_generator(response):
    for char in response:
        yield char
        await asyncio.sleep(0.02)  # Simulate typing delay

# API Endpoints
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse

# Define request schema
class QueryRequest(BaseModel):
    query: str

# FastAPI app
app = FastAPI()

@app.post("/api/query")
async def query_api(request: QueryRequest):
    """Endpoint to handle queries."""
    try:
        # Extract query from the request body
        query = request.query
        answer = rag_pipeline(query, vectorstore)  # Process the query using RAG pipeline
        
        # Streaming response for "typing effect"
        async def streaming_response_generator(response):
            for char in response:
                yield char
                await asyncio.sleep(0.02)  # Simulate typing delay

        return StreamingResponse(streaming_response_generator(answer), media_type="text/plain")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


