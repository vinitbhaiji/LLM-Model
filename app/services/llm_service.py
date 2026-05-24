import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "phi3:mini"


def generate_response(prompt):

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )

        data = response.json()

        return data.get(
            "response",
            "No response generated"
        )

    except Exception as e:

        return f"LLM error: {str(e)}"


def stream_response(prompt):

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        stream=True
    )

    for line in response.iter_lines():

        if line:

            decoded_line = line.decode(
                "utf-8"
            )

            try:

                data = json.loads(
                    decoded_line
                )

                if "response" in data:

                    yield data["response"]

            except Exception:

                continue