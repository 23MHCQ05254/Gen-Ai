
import requests

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:1b"


def check_connection():
    """Check whether the Ollama server is running."""
    try:
        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=10
        )
        response.raise_for_status()

        models = response.json().get("models", [])
        available_models = [
            model["name"] for model in models
        ]

        if not any(
            name == MODEL_NAME
            or name.startswith(MODEL_NAME + ":")
            for name in available_models
        ):
            return False, (
                f"Model {MODEL_NAME} is not downloaded. "
                "Run: ollama pull llama3.2:1b"
            )

        return True, "Ollama connected successfully."

    except requests.exceptions.ConnectionError:
        return False, (
            "Ollama is not running. "
            "Start Ollama and try again."
        )
    except requests.exceptions.RequestException as error:
        return False, f"Connection error: {error}"


def generate_response(prompt):
    """Send a prompt to Ollama and return its response."""
    if not prompt or not prompt.strip():
        raise ValueError("Please enter a prompt.")

    status, message = check_connection()

    if not status:
        raise RuntimeError(message)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt.strip(),
        "stream": False
    }

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=180
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
        if not answer:
            raise RuntimeError(
                "The model returned an empty response."
            )
        return answer
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "The model took too long to respond. Try again."
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama. "
            "Please check whether Ollama is running."
        )
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Model request failed: {error}")
def hello_world_test():
    """Verify model access with a simple test prompt."""
    prompt = (
        "Hello! Reply with 'Hello, World!' "
        "and briefly introduce yourself."
    )
    return generate_response(prompt)
if __name__ == "__main__":
    connected, message = check_connection()
    print(message)

    if connected:
        print("\nTesting model access...")
        try:
            print(hello_world_test())
        except RuntimeError as error:
            print(error)
