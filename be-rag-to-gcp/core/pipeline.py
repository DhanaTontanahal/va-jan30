from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from core.config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS
import asyncio

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

def expand_query(query: str, llm) -> str:
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

async def streaming_response_generator(response):
    """Stream the response for typing effect."""
    for char in response:
        yield char
        await asyncio.sleep(0.02)  # Simulate typing delay
