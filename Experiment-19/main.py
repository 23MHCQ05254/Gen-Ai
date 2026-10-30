
import base64
import io
import requests
from PIL import Image

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llava:latest"


def check_ollama():
    """Check whether Ollama is running and LLaVA is installed."""
    response = requests.get(
        "http://localhost:11434/api/tags",
        timeout=5
    )
    response.raise_for_status()

    models = response.json().get("models", [])
    return any(
        model.get("name", "").startswith("llava")
        for model in models
    )


def image_to_base64(image):
    """Convert an image into Base64 format."""
    image = image.convert("RGB")

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


def answer_question(image, question):
    """Generate an answer using the Ollama LLaVA model."""
    if image is None:
        raise ValueError("Please provide an image.")

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    image_data = image_to_base64(image)

    payload = {
        "model": MODEL_NAME,
        "prompt": (
            "Analyze the provided image and answer the "
            "user's question clearly and accurately. "
            "If the image does not provide enough information, "
            "say that you cannot determine the answer.\n\n"
            f"Question: {question.strip()}"
        ),
        "images": [image_data],
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=(10, 600)
    )
    response.raise_for_status()

    result = response.json()
    answer = result.get("response", "").strip()

    if not answer:
        return "The model did not return an answer."

    return answer
