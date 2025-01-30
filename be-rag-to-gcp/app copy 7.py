from langchain_community.utilities import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.llms import OpenAI  # or use any other LLM
from sqlalchemy import create_engine, text
import os
import json
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.models import QueryRequest
from core.pipeline import rag_pipeline
from core.utils import process_pdf, create_embeddings_and_vectorstore

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

# ✅ Database Configuration
DB_CONFIG = {
    "drivername": "mysql+pymysql",
    "username": "root",
    "password": "yourpassword",
    "host": "34.27.146.202",
    "port": 3306,
    "database": "menu_logger"
}

# ✅ Create Database Connection
DB_URL = f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(DB_URL)

# ✅ Initialize LangChain SQL Database
db = SQLDatabase(engine)

# ✅ Initialize LangChain SQL Agent
llm = OpenAI(model_name="gpt-4o", temperature=0.2)  # Replace with your LLM
sql_agent = create_sql_agent(llm, db=db, verbose=True)

# ✅ Initialize `vectorstore` globally (to avoid undefined errors)
vectorstore = None  # Default (will be loaded later)

# ✅ Function to Convert Query to SQL
def convert_query_to_sql(natural_language_query):
    """Uses LangChain SQL agent to convert user queries into valid SQL."""
    try:
        sql_query = sql_agent.run(natural_language_query)
        return sql_query
    except Exception as e:
        print(f"❌ SQL Agent Error: {e}")
        return None

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
    global vectorstore  # ✅ Make sure `vectorstore` is defined globally
    fetch_database_data()  # ✅ Fetch latest DB data

    # ✅ Load database JSON
    try:
        with open("core/knowledgebase/db_data.json", "r", encoding="utf-8") as f:
            db_text = json.load(f)
    except FileNotFoundError:
        print("❌ Error: `db_data.json` not found.")
        db_text = {}

    # ✅ Load PDF knowledge base
    PDF_PATH = "core/knowledgebase/knowledgebase.pdf"
    pdf_texts = process_pdf(PDF_PATH)

    # ✅ Combine database & PDF texts into embeddings
    vectorstore = create_embeddings_and_vectorstore([json.dumps(db_text)] + pdf_texts)
    print("✅ Vector store loaded successfully.")

# ✅ Load knowledge base at startup
load_knowledge_base()

# ✅ Query API - FIXED
@app.post("/api/query")
async def query_api(request: QueryRequest):
    """Handles user queries using LangChain SQL Agent for accurate data retrieval."""
    start_time = time.time()
    query = request.query

    try:
        structured_keywords = ["transactions", "credit score", "eligibility", "offers", "account balance"]
        if any(keyword in query.lower() for keyword in structured_keywords):
            print(f"🔍 Querying database for: {query}")

            # ✅ Convert natural language to SQL using LangChain
            sql_query = convert_query_to_sql(query)

            if not sql_query:
                return JSONResponse(content={"error": "Failed to generate SQL query."}, status_code=500)

            print(f"📝 Generated SQL Query: {sql_query}")

            # ✅ Execute SQL query
            with engine.connect() as connection:
                result = connection.execute(text(sql_query))
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
