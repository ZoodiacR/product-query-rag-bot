from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app.agents import build_graph, AgentState
from app.rag_pipeline import create_and_save_vector_store, get_product_documents
import os
from dotenv import load_dotenv

# --- NUEVO: Importar CORSMiddleware ---
from fastapi.middleware.cors import CORSMiddleware

# --- FIN NUEVO ---

# Cargar variables de entorno desde .env
# Esto es vital para que las variables se carguen al iniciar la app
load_dotenv()

app = FastAPI(
    title="Product Query Bot API",
    description="API for querying product information using RAG and LangGraph.",
    version="1.0.0",
)

# --- NUEVO: Configuración del Middleware CORS ---
# Permite solicitudes desde tu frontend (localhost:5173)
origins = [
    "http://localhost",
    "http://localhost:5173",  # Tu frontend de React/Vite
    # Puedes añadir otros orígenes si tu frontend se despliega en otro lugar
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista de orígenes permitidos
    allow_credentials=True,  # Permitir cookies y credenciales HTTP (si las usas)
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todas las cabeceras en las solicitudes
)
# --- FIN NUEVO ---

# Inicializar el grafo de LangGraph
# Asegúrate de que esto se ejecute después de cargar las variables de entorno
try:
    rag_graph = build_graph()
    print("Initializing LangGraph workflow...")
    # Puedes añadir un paso de calentamiento para el LLM aquí si lo deseas
    print("LangGraph workflow initialized.")
except Exception as e:
    print(f"Error initializing LangGraph workflow: {e}")
    # Considera una estrategia de reintento o salida elegante aquí
    rag_graph = None  # Asegura que el grafo no se use si no se inicializa correctamente


class QueryRequest(BaseModel):
    user_id: str
    query: str


class QueryResponse(BaseModel):
    user_id: str
    query: str
    response: str


@app.post("/query", response_model=QueryResponse)
async def query_bot(request: QueryRequest):
    """
    Receives a user query and returns a product-related response.
    """
    if rag_graph is None:
        raise HTTPException(status_code=500, detail="Bot not initialized. Check server logs.")

    print(f"Received query from user {request.user_id}: '{request.query}'")

    # Run the graph with the user's query
    # Aquí es donde se invoca tu pipeline RAG/agentes
    result = rag_graph.invoke({"query": request.query, "documents": [], "response": ""})

    # La respuesta final está en result["response"]
    final_response = result.get("response", "Lo siento, no pude procesar tu solicitud.")

    return QueryResponse(
        user_id=request.user_id,
        query=request.query,
        response=final_response
    )


@app.post("/index")
async def index_data():
    """
    Loads product data and creates/updates the FAISS vector store.
    """
    try:
        documents = get_product_documents()
        vector_store_path = os.getenv("VECTOR_STORE_PATH", "./faiss_index")

        create_and_save_vector_store(documents, vector_store_path)
        return {"message": "Data indexed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index data: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
