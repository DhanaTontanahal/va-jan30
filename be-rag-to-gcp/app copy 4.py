import os
import json
import time
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine.url import URL
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.models import QueryRequest
from core.pipeline import rag_pipeline
from core.utils import process_pdf, create_embeddings_and_vectorstore
from decimal import Decimal
from datetime import date, datetime


# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection settings       host="34.27.146.202",  
DB_CONFIG = {
    "drivername": "mysql+pymysql",
    "username": "root",          # Update with your MySQL username
    "password": "yourpassword",  # Update with your MySQL password
    "host": "34.27.146.202",         # MySQL host (localhost or IP)
    "port": 3306,                # MySQL port
    "database": "menu_logger"    # Your database name
}

# Knowledge Base JSON file path
DB_JSON_FILE = "core/knowledgebase/db_data.json"

def convert_to_serializable(obj):
    """Converts Decimal & DateTime objects for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()  # Convert Date/Datetime to "YYYY-MM-DD"
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def fetch_database_data():
    """Extracts all tables from MySQL and saves as JSON."""
    mysql_url = URL.create(**DB_CONFIG)
    engine = create_engine(mysql_url)

    try:
        with engine.connect() as connection:
            print("✅ Connected to the database.")
            
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            db_data = {}

            for table in tables:
                result = connection.execute(text(f"SELECT * FROM {table}"))
                rows = [dict(row._mapping) for row in result]
                db_data[table] = rows

            os.makedirs(os.path.dirname(DB_JSON_FILE), exist_ok=True)

            with open(DB_JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=4, default=convert_to_serializable)

            print(f"✅ Database extracted successfully to {DB_JSON_FILE}")

    except Exception as e:
        print(f"❌ Error extracting database: {e}")

# Process knowledge base at startup
def load_knowledge_base():
    """Loads PDF & database JSON into vectorstore."""
    global vectorstore

    # Extract database to JSON
    fetch_database_data()

    # Process knowledge base PDF
    KNOWLEDGE_BASE_PDF = "core/knowledgebase/knowledgebase.pdf"
    texts = process_pdf(KNOWLEDGE_BASE_PDF)

    # Process JSON database
    with open(DB_JSON_FILE, "r", encoding="utf-8") as f:
        db_text = json.load(f)
        db_texts = [json.dumps(entry) for table in db_text.values() for entry in table]
        texts.extend(db_texts)

    # Create embeddings and vector store
    vectorstore = create_embeddings_and_vectorstore(texts)

# Load data at startup
load_knowledge_base()

@app.post("/api/query")
async def query_api(request: QueryRequest):
    """Handles user queries and responds based on knowledge base and structured data."""
    start_time = time.time()
    query = request.query

    try:
        # If query is related to structured data, fetch from JSON file
        keywords = ["transactions", "credit score", "eligibility", "offers", "account balance"]
        if any(keyword in query.lower() for keyword in keywords):
            with open(DB_JSON_FILE, "r", encoding="utf-8") as f:
                db_data = json.load(f)

            relevant_data = {}
            for table, records in db_data.items():
                if any(keyword in table.lower() for keyword in keywords):
                    relevant_data[table] = records

            elapsed_time = time.time() - start_time
            return JSONResponse(content={
                "query": query,
                "sender": "assistant",
                "answer": relevant_data,
                "processing_time": f"{elapsed_time:.2f} seconds"
            }, status_code=200)

        # Otherwise, use RAG pipeline for PDF-based query
        answer = rag_pipeline(query, vectorstore)
        elapsed_time = time.time() - start_time
        return JSONResponse(content={
            "query": query,
            "sender": "assistant",
            "answer": answer,
            "processing_time": f"{elapsed_time:.2f} seconds"
        }, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
