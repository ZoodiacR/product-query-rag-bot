import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

from app.agents import build_graph
from app.rag_pipeline import create_and_save_vector_store, get_product_documents

# Load environment variables
load_dotenv()

# Pydantic model for the request body
class QueryRequest(BaseModel):
    user_id: str
    query: str

# FastAPI app instance
app = FastAPI(
    title="Product-Query Bot via RAG Pipeline",
    description="A microservice for answering product questions using a multi-agent RAG pipeline.",
    version="1.0.0"
)

# Initialize LangGraph once at startup
graph = None

@app.on_event("startup")
async def startup_event():
    """Initializes the LangGraph workflow on application startup."""
    global graph
    print("Initializing LangGraph workflow...")
    graph = build_graph()
    print("LangGraph workflow initialized.")

@app.post("/query")
async def process_query(request: QueryRequest):
    """
    Endpoint to process user queries.

    Args:
        request: A QueryRequest object containing user_id and query.

    Returns:
        A JSON response with the user's ID, query, and the bot's response.
    """
    if not graph:
        raise HTTPException(status_code=500, detail="RAG system not initialized. Please check startup logs.")

    print(f"Received query from user {request.user_id}: '{request.query}'")

    try:
        # Run the multi-agent graph
        final_state = graph.invoke({"query": request.query})
        response = final_state["response"]
        
        print(f"Generated response: '{response}'")

        return {
            "user_id": request.user_id,
            "query": request.query,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/index")
async def index_data():
    """Endpoint to trigger the data indexing process."""
    try:
        documents = get_product_documents()
        vector_store_path = os.getenv("VECTOR_STORE_PATH")
        create_and_save_vector_store(documents, vector_store_path)
        return {"message": "Indexing complete. Vector store created/updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

# This block is for local development with Uvicorn, not for Docker.
# To run locally: `uvicorn app.main:app --reload`
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
