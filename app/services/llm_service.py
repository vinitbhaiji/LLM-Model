import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "phi3:mini"


def generate_response(prompt: str) -> str:

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload
        )

        if response.status_code != 200:
            return "Error calling local model"

        return response.json()["response"]

    except Exception as e:
        return f"LLM error: {str(e)}"