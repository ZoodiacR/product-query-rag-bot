# Product-Query Bot via RAG Pipeline

This project implements a microservice that acts as a product query bot. It utilizes an advanced **Retrieval-Augmented Generation (RAG)** architecture and a multi-agent structure built with LangGraph. The bot is configured to use a **local Large Language Model (LLM) via Ollama** for response generation, allowing for a development and testing environment without external API costs.

## Features

* **FastAPI Endpoint**: A `/query` endpoint to receive user questions and an `/index` endpoint for document indexing.

* **RAG Pipeline**: A system to retrieve relevant product information from a local vector store (FAISS).

* **Local Embeddings**: Uses `HuggingFaceEmbeddings` to create document vectors, which does not require an external API key.

* **Local LLM with Ollama**: Generates responses using a language model running locally via Ollama (e.g., Llama 3).

* **Multi-Agent with LangGraph**: An architecture featuring a `Retriever Agent` (document retrieval) and a `Responder Agent` (response generation).

* **Dockerized with Docker Compose**: Both the application and the Ollama server run as Docker container services, orchestrated by Docker Compose.

* **Modular Code**: Clearly separated logic for the FastAPI app, the RAG pipeline, and the agents.

* **Unit Tests**: Basic tests for agent logic using `pytest`.

## Prerequisites

* **Docker Desktop**: Includes Docker Engine and Docker Compose.

* **Python 3.11+** (Only if you plan to run commands directly on your local machine, such as `pytest`).

## Setup and Installation

1.  **Clone the repository**:

    ```bash
    git clone [https://github.com/your-username/product-query-bot.git](https://github.com/your-username/product-query-bot.git)
    cd product-query-bot
    ```

2.  **Create and configure the `.env` file**:
    Copy the example file and fill in your details.

    ```bash
    cp .env.example .env
    ```

    Edit the `.env` file to include the following configurations. **It is crucial that there are no comments or extra spaces at the end of the `LOCAL_LLM_URL` and `LOCAL_LLM_MODEL` lines**:

    ```ini
    OPENAI_API_KEY=your_openai_api_key_here # Keep for conditional logic, will not be used if local LLM is active
    TOP_K=3
    VECTOR_STORE_PATH=./faiss_index
    LOCAL_LLM_URL=http://ollama:11434/v1 # Ollama URL within the Docker Compose network
    LOCAL_LLM_MODEL=llama3 # The model you want to use from Ollama (e.g., mistral, phi3)
    ```

    Ensure you save the `.env` file with **UTF-8 without BOM** encoding if you're using an editor like Notepad++ or Visual Studio Code.

3.  **Create the `docker-compose.yml` file**:
    In your project's root directory, create a file named `docker-compose.yml` with the following content. This will define how Docker Compose orchestrates your application and the Ollama server.

    ```yaml
    version: '3.8'

    services:
      app:
        build:
          context: .
          dockerfile: Dockerfile
        ports:
          - "8000:8000"
        environment:
          OPENAI_API_KEY: your_openai_api_key_here
          TOP_K: 3
          VECTOR_STORE_PATH: ./faiss_index
          LOCAL_LLM_URL: http://ollama:11434/v1
          LOCAL_LLM_MODEL: llama3
        depends_on:
          - ollama
        networks:
          - product_bot_network

      ollama:
        image: ollama/ollama:latest
        ports:
          - "11434:11434"
        volumes:
          - ollama_data:/root/.ollama
        networks:
          - product_bot_network

    networks:
      product_bot_network:

    volumes:
      ollama_data:
    ```

    If you prefer to copy it using PowerShell to avoid spacing issues, you can use this command:

    ```powershell
    @'
    version: '3.8'

    services:
      app:
        build:
          context: .
          dockerfile: Dockerfile
        ports:
          - "8000:8000"
        environment:
          OPENAI_API_KEY: your_openai_api_key_here
          TOP_K: 3
          VECTOR_STORE_PATH: ./faiss_index
          LOCAL_LLM_URL: http://ollama:11434/v1
          LOCAL_LLM_MODEL: llama3
        depends_on:
          - ollama
        networks:
          - product_bot_network

      ollama:
        image: ollama/ollama:latest
        ports:
          - "11434:11434"
        volumes:
          - ollama_data:/root/.ollama
        networks:
          - product_bot_network

    networks:
      product_bot_network:

    volumes:
      ollama_data:
    '@ | Out-File -FilePath "docker-compose.yml" -Encoding utf8
    ```

## Service Usage

### 1. Start Containers with Docker Compose

Ensure you are in your project's root directory and run:

```bash
docker compose up -d --build
```

This command will **build (or rebuild if there are changes) your `app` Docker image and bring up both services (`app` and `ollama`) in detached mode**. Using `--build` is crucial to ensure Docker picks up the latest changes in your code.

Wait a few seconds (or a minute) for both containers to fully start. You can verify their status with `docker ps`.

### 2. Download the Local LLM Model (only the first time or if the volume was deleted)

If this is your first time using Ollama or if you deleted the data volume (`ollama_data`), you'll need to download the LLM model you configured in your `.env` (e.g., `llama3`).

```bash
docker exec -it product-query-bot-ollama-1 ollama run llama3
```

You'll see the download progress. Once complete, press `Ctrl + C` to exit the interactive session. The model will remain saved in the Docker volume.

### 3. Index Product Data

This step creates (or updates) the FAISS vector store with embeddings of your product documents. **You must run it at least once** before making queries, and every time you add or modify your documents in `data/products`.

```bash
curl -X POST http://localhost:8000/index
```

Check the logs of your `app` container (`docker logs product-query-bot-app-1`) to confirm that `HuggingFaceEmbeddings` are being used for indexing.

### 4. Query the Bot

Once the data is indexed, you can send queries to your microservice's `/query` endpoint.

**Example with `curl`:**

```bash
curl -X POST http://localhost:8000/query \
-H "Content-Type: application/json" \
-d '{
  "user_id": "local_user_test",
  "query": "What are the main features of the 4K Ultra HD Monitor?"
}'
```

**Expect a response from the local LLM, such as:**

```json
{
  "user_id": "local_user_test",
  "query": "What are the main features of the 4K Ultra HD Monitor?",
  "response": "According to the product description, the main features of the 4K Ultra HD Monitor (MON-4K-01) are:\n\n* A resolution of 3840 x 2160 pixels\n* A fast 144Hz refresh rate and a 1ms response time, making it ideal for gaming and professional design\n* Connectivity options include DisplayPort 1.4 and two HDMI 2.1 ports\n* The stand is fully adjustable for tilt, swivel, pivot, and height\n\nThese features make the monitor suitable for demanding applications such as gaming and graphic design, while also providing a high-quality viewing experience."
}
```

You can check the logs of your `app` container (`docker logs product-query-bot-app-1`) to see the debug messages (`DEBUG:`) and confirm that `ChatOllama` is being used for response generation.

### 5. Check Service Status (Health Check)

You can check if the service is running correctly by accessing the `/health` endpoint.

```bash
curl http://localhost:8000/health
```

**Expected response:**

```json
{"status": "ok"}
```

## Running Tests

To run the unit tests, you can use the following command inside your application's container (once it's running):

```bash
docker exec -it product-query-bot-app-1 pytest tests/
```

This will execute the tests defined in `tests/test_agents.py`, ensuring your agent functions behave as expected.
