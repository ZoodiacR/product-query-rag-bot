import os
from typing import TypedDict, Annotated, Sequence, Any, List, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_community.chat_models import ChatOllama
from langchain_ollama import ChatOllama


# Define the state of the graph
class AgentState(TypedDict):
    """
    Represents the state of our multi-agent graph.

    Attributes:
        query: The user's query string.
        documents: A list of retrieved documents.
        response: The final response string.
    """
    query: str
    documents: Annotated[Sequence[Document], "Documents retrieved from vector store"]
    response: str


# --- Mock LLM Implementation (mantener para testing sin ningún LLM real) ---
'''class MockLLM(LLM):
    """
    A simple mock LLM that returns a predefined response,
    simulating that it used the context if documents were provided.
    """

    @property
    def _llm_type(self) -> str:
        return "mock_llm"

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        print(f"MockLLM received prompt:\n{prompt}")
        return "El producto consultado presenta las siguientes características destacadas: [características simuladas basadas en documentos recuperados]. Si deseas más detalles, por favor, consulta la información completa. (Respuesta generada por el LLM simulado con contexto)."

'''
# Define the nodes (agents)
def retriever_agent(state: AgentState) -> AgentState:
    """Retrieves documents based on the user's query."""
    print("---RETRIEVER AGENT---")
    query = state["query"]
    vector_store_path = os.getenv("VECTOR_STORE_PATH")
    top_k = int(os.getenv("TOP_K", 3))

    if not vector_store_path or not os.path.exists(vector_store_path):
        raise ValueError("Vector store not found. Please run the index command first.")

    from app.rag_pipeline import load_vector_store
    vector_store = load_vector_store(vector_store_path)

    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    documents = retriever.invoke(query)

    print(f"Retrieved {len(documents)} documents.")
    return {"documents": documents, "query": query, "response": ""}


def responder_agent(state: AgentState) -> AgentState:
    """Generates a response based on the retrieved documents and query."""
    print("---RESPONDER AGENT---")
    query = state["query"]
    documents = state["documents"]

    if not documents:
        # Fallback response if no documents are retrieved
        return {"query": query, "documents": [],
                "response": "Lo siento, no pude encontrar ninguna información sobre ese producto. ¿Puedes ser más específico? (Respuesta sin documentos)"}

    # Decide whether to use ChatOllama (local API), ChatOpenAI (real API), or MockLLM
    openai_api_key = os.getenv("OPENAI_API_KEY")
    local_llm_url = os.getenv("LOCAL_LLM_URL")
    local_llm_model = os.getenv("LOCAL_LLM_MODEL")

    # --- DEBUG PRINTS ---
    print(f"DEBUG: OPENAI_API_KEY='{openai_api_key}'")
    print(f"DEBUG: LOCAL_LLM_URL='{local_llm_url}'")
    print(f"DEBUG: LOCAL_LLM_MODEL='{local_llm_model}'")
    # --- FIN DEBUG PRINTS ---

    if local_llm_url and local_llm_model:
        print(f"Using ChatOllama (local LLM: {local_llm_model} at {local_llm_url})")
        llm = ChatOllama(base_url=local_llm_url, model=local_llm_model, temperature=0)
    elif openai_api_key and openai_api_key != "your_openai_api_key_here":
        print("Using ChatOpenAI (real LLM API)")
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    #else:
     #   print("Using MockLLM (simulated LLM) - No real API key or local LLM found/provided.")
      #  llm = MockLLM()

    prompt_template = """
    Eres un asistente de productos útil. Utiliza las siguientes piezas de contexto para responder a la pregunta del usuario.
    Si no sabes la respuesta, simplemente di que no tienes suficiente información, no intentes inventar una respuesta.

    Contexto:
    {context}

    Pregunta: {query}

    Respuesta:
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)

    context_str = "\n\n".join([doc.page_content for doc in documents])

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"context": context_str, "query": query})

    return {"query": query, "documents": documents, "response": response}


# Build the LangGraph
def build_graph():
    """Constructs and compiles the multi-agent graph."""
    workflow = StateGraph(AgentState)
    workflow.add_node("retriever", retriever_agent)
    workflow.add_node("responder", responder_agent)

    workflow.set_entry_point("retriever")
    workflow.add_edge("retriever", "responder")
    workflow.add_edge("responder", END)

    return workflow.compile()