import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
local_llm_url = os.getenv("LOCAL_LLM_URL")
local_llm_model = os.getenv("LOCAL_LLM_MODEL")

    # --- DEBUG PRINTS ---
print(f"DEBUG: OPENAI_API_KEY='{openai_api_key}'")
print(f"DEBUG: LOCAL_LLM_URL='{local_llm_url}'")
print(f"DEBUG: LOCAL_LLM_MODEL='{local_llm_model}'")
    # --- FIN DEBUG PRINTS ---
