
import requests

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:1b"


def check_connection():
    """Check Ollama connection and model availability."""
    try:
        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=10
        )
        response.raise_for_status()

        models = response.json().get("models", [])
        available_models = [m["name"] for m in models]

        if not any(
            name == MODEL_NAME
            or name.startswith(MODEL_NAME + ":")
            for name in available_models
        ):
            return False, (
                f"Model not found: {MODEL_NAME}. "
                f"Run: ollama pull {MODEL_NAME}"
            )

        return True, "Ollama connected successfully."

    except requests.exceptions.RequestException as error:
        return False, f"Connection failed: {error}"


def generate_response(prompt):
    """Generate an answer using Ollama."""
    if not prompt or not prompt.strip():
        raise ValueError("Please enter a prompt.")

    connected, message = check_connection()
    if not connected:
        raise RuntimeError(message)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt.strip(),
        "stream": False,
        "options": {
            "temperature": 0.2
        }
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
            raise RuntimeError("The model returned an empty answer.")

        return answer

    except requests.exceptions.Timeout:
        raise RuntimeError(
            "The model took too long to respond. Try again."
        )
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Generation failed: {error}")


def compare_responses(baseline_prompt, enhanced_prompt):
    """Generate and return both answers for comparison."""
    baseline_answer = generate_response(baseline_prompt)
    enhanced_answer = generate_response(enhanced_prompt)

    return baseline_answer, enhanced_answer


if __name__ == "__main__":
    connected, message = check_connection()
    print(message)

    if connected:
        print("\nTesting model...")
        print(generate_response("Explain AI in one sentence."))
