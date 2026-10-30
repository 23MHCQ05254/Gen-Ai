
import requests

BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:1b"
TIMEOUT = 300


class OllamaError(Exception):
    pass


def check_connection():
    """Check whether Ollama is running and the model is available."""
    try:
        response = requests.get(
            f"{BASE_URL}/api/tags",
            timeout=10
        )
        response.raise_for_status()

        models = response.json().get("models", [])

        for model in models:
            name = model.get("name", "")
            if name == MODEL_NAME or name.startswith(MODEL_NAME + ":"):
                return True

        raise OllamaError(
            f"Model '{MODEL_NAME}' is not installed. "
            f"Run: ollama pull {MODEL_NAME}"
        )

    except requests.RequestException as error:
        raise OllamaError(
            "Cannot connect to Ollama. Open a terminal and run "
            "'ollama serve', if Ollama is not already running."
        ) from error


ZERO_SHOT_TEMPLATE = """
You are a helpful academic tutor.

Answer the student's question in simple English.
Keep the explanation clear and suitable for a college student.
Answer in a few sentences.
Do not include a separate example unless it is necessary.

Student question:
{user_question}

Answer:
"""


FEW_SHOT_EXAMPLES = """
You are a helpful academic tutor.

Study the following examples to understand the expected answer style.
Give a simple definition followed by a concrete example.

Question: What is gravity?
Response: Gravity is the force that attracts objects toward each other.
Example: Gravity makes an apple fall from a tree.

Question: What is photosynthesis?
Response: Photosynthesis is the process by which green plants make food
using sunlight, water, and carbon dioxide.
Example: A green plant uses sunlight to prepare food in its leaves.

Question: What is a data structure?
Response:
"""


def generate_response(prompt):
    """Generate one response using the local Ollama model."""
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3
                }
            },
            timeout=TIMEOUT
        )

        response.raise_for_status()
        result = response.json().get("response", "").strip()

        if not result:
            raise OllamaError("Ollama returned an empty response.")

        return result

    except requests.RequestException as error:
        raise OllamaError(
            f"Failed to generate a response using Ollama: {error}"
        ) from error


def compare_prompts(user_question):
    """Compare zero-shot and few-shot prompting on the same question."""
    question = user_question.strip()

    if not question:
        raise ValueError("Please enter a question.")

    check_connection()

    zero_prompt = ZERO_SHOT_TEMPLATE.format(
        user_question=question
    )

    few_prompt = (
        FEW_SHOT_EXAMPLES
        + question
        + "\nResponse:\n"
    )

    zero_response = generate_response(zero_prompt)
    few_response = generate_response(few_prompt)

    return (
        zero_response,
        few_response,
        zero_prompt,
        few_prompt
    )


if __name__ == "__main__":
    try:
        question = input("Enter your question: ")

        zero, few, _, _ = compare_prompts(question)

        print("\n--- ZERO-SHOT RESPONSE ---")
        print(zero)

        print("\n--- FEW-SHOT RESPONSE ---")
        print(few)

        print("\n--- COMPARISON ---")
        print("Zero-shot: The model receives instructions without examples.")
        print("Few-shot: The model receives examples before the question.")

    except (OllamaError, ValueError) as error:
        print("Error:", error)
