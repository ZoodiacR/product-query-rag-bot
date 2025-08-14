import pytest
import os
from unittest.mock import patch, MagicMock
from app.agents import retriever_agent, responder_agent, AgentState
from langchain_core.documents import Document

# Mock environment variables for testing
os.environ["VECTOR_STORE_PATH"] = "./test_faiss_index"
os.environ["TOP_K"] = "2"

@pytest.fixture(scope="module")
def sample_vector_store():
    """
    Mocks a FAISS vector store for testing.
    """
    mock_doc1 = Document(page_content="Product 1 description.")
    mock_doc2 = Document(page_content="Product 2 description.")
    mock_vector_store = MagicMock()
    mock_vector_store.as_retriever.return_value.invoke.return_value = [mock_doc1, mock_doc2]
    return mock_vector_store

@patch("app.rag_pipeline.load_vector_store")
def test_retriever_agent_retrieves_documents(mock_load_vector_store, sample_vector_store):
    """
    Tests if the retriever agent correctly invokes the vector store to get documents.
    """
    # Arrange
    mock_load_vector_store.return_value = sample_vector_store
    initial_state = AgentState(query="What are the features of product 1?", documents=[], response="")
    
    # Act
    result_state = retriever_agent(initial_state)
    
    # Assert
    assert "documents" in result_state
    assert len(result_state["documents"]) == 2
    assert result_state["query"] == initial_state["query"]
    mock_load_vector_store.assert_called_once_with(os.getenv("VECTOR_STORE_PATH"), allow_dangerous_deserialization=True)

@patch("app.agents.ChatOpenAI")
def test_responder_agent_generates_response(mock_openai):
    """
    Tests if the responder agent generates a response using the LLM.
    """
    # Arrange
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = "This is a mocked response."
    mock_openai.return_value = mock_llm_instance
    
    mock_docs = [
        Document(page_content="This is the context for the query."),
        Document(page_content="This is more context.")
    ]
    initial_state = AgentState(query="What is the product?", documents=mock_docs, response="")

    # Act
    result_state = responder_agent(initial_state)
    
    # Assert
    assert "response" in result_state
    assert result_state["response"] == "This is a mocked response."
    mock_openai.assert_called_once()
    mock_llm_instance.invoke.assert_called_once()

def test_responder_agent_handles_no_documents():
    """
    Tests the fallback response when no documents are found.
    """
    # Arrange
    initial_state = AgentState(query="What is the product?", documents=[], response="")
    
    # Act
    result_state = responder_agent(initial_state)
    
    # Assert
    expected_response = "Sorry, I couldn't find any information about that product. Can you please be more specific?"
    assert result_state["response"] == expected_response
