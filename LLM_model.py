# LLM_model.py

# Define Ollama model hyperparameters
OLLAMA_MODEL_CONFIG = {
    "model": "qwq:latest",  # Model name    
    "max_tokens": 1024,     # Maximum tokens in the response
    "ctx_window_size": 4096 # Context window size
}