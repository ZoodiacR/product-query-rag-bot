# Product-Query Bot via RAG Pipeline

This project implements a microservice that acts as a product query bot. It utilizes an advanced **Retrieval-Augmented Generation (RAG)** architecture and a multi-agent structure built with LangGraph. The bot is configured to use a **local Large Language Model (LLM) via Ollama** for response generation, allowing for a development and testing environment without external API costs. It also includes a **React frontend** for a user-friendly interface.

## Features

* **FastAPI Backend**: A `/query` endpoint to receive user questions and an `/index` endpoint for document indexing.
* **React Frontend**: A responsive, minimalist Single Page Application (SPA) built with React, Vite, Tailwind CSS, and Lucide React icons, served by Nginx.
* **RAG Pipeline**: A system to retrieve relevant product information from a local vector store (FAISS).
* **Local Embeddings**: Uses `HuggingFaceEmbeddings` to create document vectors, requiring no external API key.
* **Local LLM with Ollama**: Generates responses using a language model (e.g., Llama 3) running locally via an Ollama Docker container.
* **Multi-Agent with LangGraph**: An architecture featuring a `Retriever Agent` (document retrieval) and a `Responder Agent` (response generation).
* **Dockerized with Docker Compose**: Both the backend API, the frontend application, and the Ollama server run as Docker container services, orchestrated by Docker Compose.
* **Modular Code**: Clearly separated logic for the FastAPI app, the React app, the RAG pipeline, and the agents.
* **Unit Tests**: Basic tests for agent logic using `pytest`.

## Prerequisites

* **Docker Desktop**: Includes Docker Engine and Docker Compose.
* **Node.js & npm** (or Yarn/pnpm): Required for local frontend development (installing dependencies, running dev server).
* **Python 3.11+** (Only if you plan to run backend commands directly on your host machine, like `pytest`).

## Setup and Installation

1.  **Clone the repository**:
    Start by cloning the entire project structure.

    ```bash
    git clone [https://github.com/your-username/product-query-bot.git](https://github.com/your-username/product-query-bot.git)
    cd product-query-bot
    ```
    *(Note: This assumes `product-query-bot` will be the parent directory containing both `product-query-bot-backend` and `product-query-bot-frontend`. Adjust paths if your root project directory is named differently.)*

2.  **Organize Project Structure**:
    Create a `product-query-bot-frontend` directory at the same level as `product-query-bot` (your backend).
    Move your backend files into a dedicated `product-query-bot-backend` directory.

    ```bash
    # Assuming you are in the root of your cloned project (e.g., C:\Proyectos\proyecto prueba\product-query-bot)
    # Rename your existing backend folder for clarity
    cd .. # Go up one level to C:\Proyectos\proyecto prueba
    Rename-Item product-query-bot product-query-bot-backend

    # Create the frontend folder (if you haven't already done so)
    New-Item -ItemType Directory -Path "product-query-bot-frontend"

    # Now navigate into the backend folder to rename its Dockerfile
    cd product-query-bot-backend
    Rename-Item Dockerfile Dockerfile.backend
    cd .. # Go back to C:\Proyectos\proyecto prueba
    ```

3.  **Create and Configure the `.env` file**:
    Create `.env` file in the **`product-query-bot-backend`** directory.

    ```bash
    # From C:\Proyectos\proyecto prueba\
    cd product-query-bot-backend
    cp .env.example .env
    ```
    Edit the `.env` file to contain the following configurations. **It is crucial that there are no comments or extra spaces at the end of the `LOCAL_LLM_URL` and `LOCAL_LLM_MODEL` lines**:

    ```ini
    OPENAI_API_KEY=your_openai_api_key_here # Keep for conditional logic, will not be used if local LLM is active
    TOP_K=3
    VECTOR_STORE_PATH=./faiss_index
    LOCAL_LLM_URL=http://ollama:11434 # Ollama URL within the Docker Compose network
    LOCAL_LLM_MODEL=llama3 # The model you want to use from Ollama (e.g., mistral, phi3)
    ```
    Ensure you save the `.env` file with **UTF-8 without BOM** encoding if you're using an editor like Notepad++ or Visual Studio Code.

4.  **Create Frontend Dockerfile and Nginx Config**:
    Navigate into your `product-query-bot-frontend` directory.

    ```bash
    # From C:\Proyectos\proyecto prueba\
    cd product-query-bot-frontend
    ```
    Create `Dockerfile` in `product-query-bot-frontend` (this will build your React app and serve it with Nginx):

    ```dockerfile
    # Stage 1: Build the React application
    FROM node:20-alpine AS build

    WORKDIR /app
    COPY package*.json ./
    RUN npm install
    COPY . .
    RUN npm run build

    # Stage 2: Serve the application with Nginx for production-ready serving
    FROM nginx:alpine
    RUN rm /etc/nginx/conf.d/default.conf
    COPY nginx.conf /etc/nginx/conf.d/default.conf
    COPY --from=build /app/dist /usr/share/nginx/html
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]
    ```
    Create `nginx.conf` in `product-query-bot-frontend` (crucial for SPA routing):

    ```nginx
    server {
      listen 80;
      server_name localhost;
      location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
      }
      error_page 500 502 503 504 /50x.html;
      location = /50x.html {
        root /usr/share/nginx/html;
      }
    }
    ```
    *(Note: You can use `Out-File` PowerShell commands for these if you prefer, similar to how `.env` was created previously.)*

5.  **Create the Central `docker-compose.yml`**:
    Navigate to the **root** of your overall project (e.g., `C:\Proyectos\proyecto prueba\`).

    ```bash
    # From C:\Proyectos\proyecto prueba\product-query-bot-frontend (or backend)
    cd ..
    ```
    Create a new `docker-compose.yml` file here with the following content:

    ```yaml
    version: '3.8' # The "obsolete" warning is normal, it's ignored.

    services:
      # 1. Backend Service (FastAPI API + Ollama)
      backend:
        build:
          context: ./product-query-bot-backend # Build context points to your backend folder
          dockerfile: Dockerfile.backend # The renamed backend Dockerfile
        ports:
          - "8000:8000" # Map host port 8000 to container port
        environment: # Environment variables for the backend
          OPENAI_API_KEY: your_openai_api_key_here
          TOP_K: 3
          VECTOR_STORE_PATH: ./faiss_index
          LOCAL_LLM_URL: http://ollama:11434 # Internal communication between containers
          LOCAL_LLM_MODEL: llama3
        depends_on:
          - ollama # Ensure Ollama starts first
        networks:
          - product_bot_network # Both services on the same network

      # 2. Frontend Service (React Application)
      frontend:
        build:
          context: ./product-query-bot-frontend # Build context points to your frontend folder
          dockerfile: Dockerfile # The frontend Dockerfile
        ports:
          - "5173:80" # Map host port 5173 to Nginx's port 80 in the container
        depends_on:
          - backend # Frontend depends on backend for API calls
        networks:
          - product_bot_network

      # 3. Ollama Service (Local LLM Server)
      ollama:
        image: ollama/ollama:latest # Official Ollama image
        ports:
          - "11434:11434" # Map host port 11434 to container port
        volumes:
          - ollama_data:/root/.ollama # Volume to persist downloaded models
        networks:
          - product_bot_network

    # Network and volume definitions
    networks:
      product_bot_network: # Custom network for internal service communication

    volumes:
      ollama_data: # Volume for Ollama data
    ```

## Service Usage

### 1. Start All Containers with Docker Compose

Ensure your terminal is in the **root directory** of your overall project (e.g., `C:\Proyectos\proyecto prueba\`) and run:

```bash
docker compose up -d --build
```

This command will **build (or rebuild if there are changes) both your `backend` and `frontend` Docker images and bring up all three services (`backend`, `frontend`, and `ollama`) in detached mode**. Using `--build` is crucial to ensure Docker picks up the latest changes in your code.

Allow a few seconds (or a minute) for all containers to fully start. You can verify their status with `docker ps`.

### 2. Download the Local LLM Model (only the first time or if the volume was deleted)

If this is your first time using Ollama, or if you performed a `docker compose down --volumes` previously, you'll need to download the LLM model configured in your `.env` (e.g., `llama3`).

```bash
docker exec -it product-query-bot-ollama-1 ollama run llama3
```

You'll see the download progress. Once complete, press `Ctrl + C` to exit the interactive session. The model will remain saved in the Docker volume.

### 3. Index Product Data (Backend)

This step creates (or updates) the FAISS vector store with embeddings of your product documents. **You must run it at least once** before making queries, and every time you add or modify your documents in `data/products`.

```bash
curl -X POST http://localhost:8000/index
```

Check the logs of your `backend` container (`docker logs product-query-bot-backend-1`) to confirm that `HuggingFaceEmbeddings` are being used for indexing.

### 4. Access Your Frontend Application

Once all services are up and the backend data is indexed, open your web browser and navigate to:

[http://localhost:5173](http://localhost:5173)

You should see your React application's minimalist interface. Enter a product query, and the frontend will communicate with your backend, which in turn will use the local Ollama LLM to generate the response.

You can check the logs of your `backend` container (`docker logs product-query-bot-backend-1`) to see debug messages and confirm that `ChatOllama` is being used for response generation.

### 5. Check Service Status (Health Check)

You can check if the backend service is running correctly by accessing its `/health` endpoint.

```bash
curl http://localhost:8000/health
```

**Expected response:**

```json
{"status": "ok"}
```

## Running Tests

To run the unit tests for the backend agents, you can use the following command inside your backend application's container (once it's running):

```bash
docker exec -it product-query-bot-backend-1 pytest tests/
```

This will execute the tests defined in `tests/test_agents.py`, ensuring your agent functions behave as expected.