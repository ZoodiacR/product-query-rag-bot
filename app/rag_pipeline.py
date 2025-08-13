import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings  # <-- Importar nueva clase
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings



def get_product_documents():
    """Loads product documents from the data directory."""
    documents = []
    data_dir = os.path.join(os.getcwd(), "data", "products")
    for file_name in os.listdir(data_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(data_dir, file_name)
            loader = TextLoader(file_path)
            documents.extend(loader.load())
    return documents


def create_and_save_vector_store(documents, vector_store_path):
    """
    Creates a FAISS vector store from documents and saves it to disk.

    Args:
        documents: A list of LangChain Document objects.
        vector_store_path: The path to save the vector store.
    """
    if not os.path.exists(vector_store_path):
        os.makedirs(vector_store_path)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)

    # Decide whether to use OpenAIEmbeddings or HuggingFaceEmbeddings
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and openai_api_key != "your_openai_api_key_here":  # Check if it's a real key
        print("Using OpenAIEmbeddings (real API)")
        embeddings = OpenAIEmbeddings()
    else:
        print("Using HuggingFaceEmbeddings (local model) - No real OpenAI API key found or provided.")
        # Usamos un modelo de sentence-transformers. Puedes elegir otros si lo deseas.
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_store = FAISS.from_documents(split_docs, embeddings)
    vector_store.save_local(vector_store_path)
    print(f"Vector store saved to {vector_store_path}")


def load_vector_store(vector_store_path):
    """
    Loads an existing FAISS vector store from disk.

    Args:
        vector_store_path: The path where the vector store is saved.

    Returns:
        FAISS: The loaded FAISS vector store object.
    """
    # Needs to load with the same type of embeddings used to save it
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and openai_api_key != "your_openai_api_key_here":  # Check if it's a real key
        embeddings = OpenAIEmbeddings()
    else:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    return FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
