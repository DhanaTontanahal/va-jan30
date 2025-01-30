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
KNOWLEDGE_BASE_PDF = "core/knowledgebase/knowledgebase.pdf"
CURRENT_USER_ID = 101101  # Set current user ID globally


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

# Function to load both JSON & PDF into vector store
def load_knowledge_base():
    """Loads both structured (DB JSON) and unstructured (PDF) data into the vector store."""
    global vectorstore

    # Step 1: Extract database to JSON
    fetch_database_data()

    # Step 2: Load Knowledge Base PDF
    pdf_texts = process_pdf(KNOWLEDGE_BASE_PDF)

    # Step 3: Load JSON database
    with open(DB_JSON_FILE, "r", encoding="utf-8") as f:
        db_text = json.load(f)
        db_texts = [json.dumps(entry) for table in db_text.values() for entry in table]

    # Step 4: Combine Both Text Sources
    all_texts = pdf_texts + db_texts

    # Step 5: Create embeddings and vector store
    vectorstore = create_embeddings_and_vectorstore(all_texts)
    print("✅ Vector store initialized with both DB & PDF knowledge.")

# Load data at startup
load_knowledge_base()

# @app.post("/api/query")
# async def query_api(request: QueryRequest):
#     """Handles user queries and responds based on structured (DB) and unstructured (PDF) data."""
#     start_time = time.time()
#     query = request.query

#     try:
#         # If query is related to structured data, fetch from Vector Store (DB JSON)
#         structured_keywords = ["transactions", "credit score", "eligibility", "offers", "account balance"]
#         if any(keyword in query.lower() for keyword in structured_keywords):
#             with open(DB_JSON_FILE, "r", encoding="utf-8") as f:
#                 db_data = json.load(f)

#             relevant_data = {}
#             for table, records in db_data.items():
#                 if any(keyword in table.lower() for keyword in structured_keywords):
#                     relevant_data[table] = records

#             elapsed_time = time.time() - start_time
#             return JSONResponse(content={
#                 "query": query,
#                 "sender": "assistant",
#                 "answer": relevant_data,
#                 "processing_time": f"{elapsed_time:.2f} seconds"
#             }, status_code=200)

#         # Otherwise, use RAG pipeline for knowledge base queries (PDF)
#         answer = rag_pipeline(query, vectorstore)
#         elapsed_time = time.time() - start_time
#         return JSONResponse(content={
#             "query": query,
#             "sender": "assistant",
#             "answer": answer,
#             "processing_time": f"{elapsed_time:.2f} seconds"
#         }, status_code=200)

#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)


# @app.post("/api/query")
# async def query_api(request: QueryRequest):
#     """Handles user queries and returns personalized data for the current user."""
#     start_time = time.time()
#     query = request.query

#     try:
#         # Structured data keywords (DB JSON)
#         structured_keywords = ["transactions", "credit score", "eligibility", "offers", "account balance"]

#         if any(keyword in query.lower() for keyword in structured_keywords):
#             with open(DB_JSON_FILE, "r", encoding="utf-8") as f:
#                 db_data = json.load(f)

#             relevant_data = {}
#             for table, records in db_data.items():
#                 if any(keyword in table.lower() for keyword in structured_keywords):
#                     # Filter records for the current user only
#                     filtered_records = [record for record in records if record.get("user_id") == CURRENT_USER_ID or record.get("UserID") == CURRENT_USER_ID]
#                     if filtered_records:
#                         relevant_data[table] = filtered_records

#             elapsed_time = time.time() - start_time
#             return JSONResponse(content={
#                 "query": query,
#                 "sender": "assistant",
#                 "answer": relevant_data,
#                 "processing_time": f"{elapsed_time:.2f} seconds"
#             }, status_code=200)

#         # Otherwise, use the vector store (PDF knowledge)
#         answer = rag_pipeline(query, vectorstore)
#         elapsed_time = time.time() - start_time
#         return JSONResponse(content={
#             "query": query,
#             "sender": "assistant",
#             "answer": answer,
#             "processing_time": f"{elapsed_time:.2f} seconds"
#         }, status_code=200)

#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)


# def transform_response_to_text(data):
#     """Formats JSON data into a user-friendly text summary."""

#     summary = ""

#     # ✅ Process Transactions
#     if "transactions" in data:
#         summary += "Your recent transactions:\n"
#         for txn in data["transactions"]:
#             summary += f"- {txn['transaction_type']} of ${txn['transaction_amount']} on {txn['transaction_datetime']}\n"

#     # ✅ Process Credit Score Offers
#     if "CreditScoreOffers" in data:
#         summary += "\nYou have the following credit score offers:\n"
#         for offer in data["CreditScoreOffers"]:
#             summary += f"- {offer['OfferDescription']} (Min Score: {offer['MinCreditScore']})\n"

#     # ✅ Process Credit Card Eligibility
#     if "CreditCardEligibility" in data:
#         summary += "\nYou are eligible for the following credit cards:\n"
#         for card in data["CreditCardEligibility"]:
#             summary += f"- {card['CardType']}\n"

#     # ✅ Process Product Eligibility
#     if "UserProductEligibility" in data:
#         summary += "\nBased on your credit score, you qualify for:\n"
#         for product in data["UserProductEligibility"]:
#             summary += f"- Product ID {product['ProductID']}\n"

#     return summary if summary else "No relevant data found."


# @app.post("/api/query")
# async def query_api(request: QueryRequest):
#     """Handles user queries and formats the response using an LLM."""
#     start_time = time.time()
#     query = request.query

#     try:
#         # Structured data keywords (DB JSON)
#         structured_keywords = ["transactions", "credit score", "eligibility", "offers", "account balance"]

#         if any(keyword in query.lower() for keyword in structured_keywords):
#             with open(DB_JSON_FILE, "r", encoding="utf-8") as f:
#                 db_data = json.load(f)

#             relevant_data = {}
#             for table, records in db_data.items():
#                 if any(keyword in table.lower() for keyword in structured_keywords):
#                     # Filter records for the current user only
#                     filtered_records = [record for record in records if record.get("user_id") == CURRENT_USER_ID or record.get("UserID") == CURRENT_USER_ID]
#                     if filtered_records:
#                         relevant_data[table] = filtered_records

#             # ✅ Step 2: Convert structured data into a human-readable format
#             formatted_text = transform_response_to_text(relevant_data)

#             # ✅ Step 3: Use LLM to generate a user-friendly response
#             answer = rag_pipeline(f"Summarize this for a user: {formatted_text}", vectorstore)

#             elapsed_time = time.time() - start_time
#             return JSONResponse(content={
#                 "query": query,
#                 "sender": "assistant",
#                 "answer": answer,
#                 "processing_time": f"{elapsed_time:.2f} seconds"
#             }, status_code=200)

#         # Otherwise, use the vector store (PDF knowledge)
#         answer = rag_pipeline(query, vectorstore)
#         elapsed_time = time.time() - start_time
#         return JSONResponse(content={
#             "query": query,
#             "sender": "assistant",
#             "answer": answer,
#             "processing_time": f"{elapsed_time:.2f} seconds"
#         }, status_code=200)

#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)

def transform_response_to_text(data, user_credit_score=None):
    print (data)
    """Formats JSON data into a user-friendly text summary, ensuring credit score is included."""

    summary = ""

    # ✅ Add Credit Score First
    if user_credit_score:
        summary += f"Your current credit score is **{user_credit_score}**.\n"

    # ✅ Process Transactions
    if "transactions" in data:
        summary += "\nYour recent transactions:\n"
        for txn in data["transactions"][:5]:  # Show only last 5 transactions
            summary += f"- {txn['transaction_type']} of ${txn['transaction_amount']} on {txn['transaction_datetime']}\n"

    # ✅ Process Credit Score Offers
    if "CreditScoreOffers" in data:
        summary += "\nYou have the following credit score offers:\n"
        for offer in data["CreditScoreOffers"]:
            summary += f"- {offer['OfferDescription']} (Min Score: {offer['MinCreditScore']})\n"

    # ✅ Process Credit Card Eligibility
    if "CreditCardEligibility" in data:
        summary += "\nYou are eligible for the following credit cards:\n"
        for card in data["CreditCardEligibility"]:
            summary += f"- {card['CardType']}\n"

    # ✅ Process Product Eligibility
    if "UserProductEligibility" in data:
        summary += "\nBased on your credit score, you qualify for:\n"
        for product in data["UserProductEligibility"]:
            summary += f"- Product ID {product['ProductID']}\n"

    return summary if summary else "No relevant data found."



@app.post("/api/query")
async def query_api(request: QueryRequest):
    """Handles user queries and ensures the credit score is included in responses."""
    start_time = time.time()
    query = request.query

    try:
        structured_keywords = ["transactions", "credit score", "eligibility", "offers", "account balance"]

        if any(keyword in query.lower() for keyword in structured_keywords):
            with open(DB_JSON_FILE, "r", encoding="utf-8") as f:
                db_data = json.load(f)

            relevant_data = {}
            user_credit_score = None  # Placeholder for credit score

            for table, records in db_data.items():
                if any(keyword in table.lower() for keyword in structured_keywords):
                    filtered_records = [record for record in records if record.get("user_id") == CURRENT_USER_ID or record.get("UserID") == CURRENT_USER_ID]
                    if filtered_records:
                        relevant_data[table] = filtered_records

            # ✅ Step 2: Extract Credit Score (If Available)
            if "CreditScores" in db_data:
                user_credit_score = next(
                    (record["credit_score"] for record in db_data["CreditScores"] if record["UserID"] == CURRENT_USER_ID), 
                    None
                )

            # ✅ Step 3: Estimate Credit Score from Offers (If Missing)
            if user_credit_score is None and "CreditScoreOffers" in relevant_data:
                min_score = min(offer["MinCreditScore"] for offer in relevant_data["CreditScoreOffers"])
                user_credit_score = min_score  # Assume user qualifies for the lowest possible offer

            # ✅ Step 4: Convert structured data into text with the credit score included
            formatted_text = transform_response_to_text(relevant_data, user_credit_score)

            # ✅ Step 5: Use LLM to generate a user-friendly response
            answer = rag_pipeline(f"Summarize this for a user: {formatted_text}", vectorstore)

            elapsed_time = time.time() - start_time
            return JSONResponse(content={
                "query": query,
                "sender": "assistant",
                "answer": answer,
                "processing_time": f"{elapsed_time:.2f} seconds"
            }, status_code=200)

        # Otherwise, use the vector store (PDF knowledge)
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
