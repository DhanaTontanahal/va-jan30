from langchain_community.agent_toolkits import SQLDatabaseToolkit
# from langchain.sql_database import SQLDatabase
from langchain_openai import OpenAI
import os
import json
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.models import QueryRequest
from core.pipeline import rag_pipeline
from core.utils import process_pdf, create_embeddings_and_vectorstore
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, text  # ✅ Import text function


# ✅ Initialize FastAPI
app = FastAPI()

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Database Connection
DB_URL = "mysql+pymysql://root:yourpassword@34.27.146.202/menu_logger"
engine = create_engine(DB_URL)


# ✅ Initialize LangChain SQL Toolkit
db = SQLDatabase(engine)
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)

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
KNOWLEDGE_BASE_PDF = "core/knowledgebase/knowledgebase.pdf"
CURRENT_USER_ID = 101101  # Set current user ID globally


def convert_to_serializable(obj):
    """Converts Decimal & DateTime objects for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()  # Convert Date/Datetime to "YYYY-MM-DD"
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# ✅ Function to Fetch Database Data
def fetch_database_data():
    """Fetches all tables and their data and saves to a JSON file."""
    try:
        with engine.connect() as connection:
            print("✅ Connected to the database.")

            tables = connection.execute(text("SHOW TABLES")).fetchall()
            db_data = {}

            for (table_name,) in tables:
                result = connection.execute(text(f"SELECT * FROM {table_name}"))
                db_data[table_name] = [dict(row._mapping) for row in result]

            # ✅ Save JSON file
            with open("core/knowledgebase/db_data.json", "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=4, default=str)

            print("✅ Database data saved successfully.")

    except Exception as e:
        print(f"❌ Error extracting database: {e}")

# ✅ Function to Load Knowledge Base
def load_knowledge_base():
    """Loads database & PDF knowledge base into vector store."""
    fetch_database_data()  # ✅ Fetch latest DB data
    db_text = json.load(open("core/knowledgebase/db_data.json", "r", encoding="utf-8"))
    vectorstore = create_embeddings_and_vectorstore([json.dumps(db_text)])

    return vectorstore

# ✅ Load knowledge base on startup
vectorstore = load_knowledge_base()

def transform_response_to_text(data):
    """Formats SQL query results into a user-friendly text summary."""
    summary = ""

    if isinstance(data, list) and len(data) > 0:
        # ✅ If "credit_score" field exists, return it first
        if "credit_score" in data[0]:
            summary += f"Your current credit score is **{data[0]['credit_score']}**.\n"

        # ✅ Process transactions
        for row in data:
            if "transaction_type" in row:
                summary += f"- {row['transaction_type']} of ${row['transaction_amount']} on {row['transaction_datetime']}\n"

        # ✅ Process credit card eligibility
        if "CardType" in data[0]:
            summary += "\nYou are eligible for the following credit cards:\n"
            for row in data:
                summary += f"- {row['CardType']}\n"

    return summary if summary else "No relevant data found."




@app.post("/api/query")
async def query_api(request: QueryRequest):
    """Handles user queries using SQLDatabaseToolkit for accurate data retrieval."""
    start_time = time.time()
    query = request.query

    try:
        # ✅ If the query is structured, use SQLDatabaseToolkit
        structured_keywords = ["transactions", "credit score", "eligibility", "offers", "account balance"]
        if any(keyword in query.lower() for keyword in structured_keywords):
            print(f"🔍 Querying database for: {query}")

            # ✅ Use LangChain to generate SQL query dynamically
            sql_query = db.run(query)
            print(f"📝 Generated SQL Query: {sql_query}")

            # ✅ Execute SQL query
            with engine.connect() as connection:
                result = connection.execute(sql_query)
                data = [dict(row._mapping) for row in result]

            # ✅ Convert to human-readable format
            formatted_text = transform_response_to_text(data)

            # ✅ Use LLM to summarize the structured response
            answer = rag_pipeline(f"Summarize this for a user: {formatted_text}", vectorstore)

            elapsed_time = time.time() - start_time
            return JSONResponse(content={
                "query": query,
                "sender": "assistant",
                "answer": answer,
                "processing_time": f"{elapsed_time:.2f} seconds"
            }, status_code=200)

        # ✅ Otherwise, use the vector store (for general knowledge queries)
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
