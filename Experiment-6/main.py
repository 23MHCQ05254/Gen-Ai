
import requests

BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:1b"
TIMEOUT = 300


class OllamaError(Exception):
    """Raised when Ollama cannot generate a response."""
    pass


def check_connection():
    """Check Ollama connection and model availability."""
    try:
        response = requests.get(
            f"{BASE_URL}/api/tags",
            timeout=10
        )
        response.raise_for_status()

        models = response.json().get("models", [])
        installed = any(
            model.get("name", "").split(":")[0] == MODEL_NAME.split(":")[0]
            for model in models
        )

        if not installed:
            raise OllamaError(
                f"Model '{MODEL_NAME}' is not installed. "
                f"Run: ollama pull {MODEL_NAME}"
            )

        return True

    except requests.RequestException as error:
        raise OllamaError(
            "Cannot connect to Ollama. Make sure Ollama is running."
        ) from error


def generate_response(prompt):
    """Generate a response using the local Ollama model."""
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
        answer = response.json().get("response", "").strip()

        if not answer:
            raise OllamaError("Ollama returned an empty response.")

        return answer

    except requests.RequestException as error:
        raise OllamaError(
            f"Response generation failed: {error}"
        ) from error


def evaluate_prompts(question, role, negative_instruction):
    """
    Generate normal, role-based, and role-plus-negative responses.
    """
    question = question.strip()
    role = role.strip()
    negative_instruction = negative_instruction.strip()

    if not question:
        raise ValueError("Please enter a question.")

    if not role:
        raise ValueError("Please enter a role-based instruction.")

    if not negative_instruction:
        raise ValueError("Please enter a negative instruction.")

    check_connection()

    # 1. Normal prompt
    normal_prompt = question

    # 2. Role-based prompt
    role_prompt = (
        f"{role}\n\n"
        "Answer the following question clearly and accurately.\n\n"
        f"Question: {question}\n"
        "Answer:"
    )

    # 3. Role-based prompt with negative instructions
    controlled_prompt = (
        f"{role}\n\n"
        "Answer the following question clearly and accurately.\n"
        f"Restrictions: {negative_instruction}\n"
        "Follow the restrictions as closely as possible while "
        "providing a useful and accurate answer.\n\n"
        f"Question: {question}\n"
        "Answer:"
    )

    # Generate all three responses
    normal_response = generate_response(normal_prompt)
    role_response = generate_response(role_prompt)
    controlled_response = generate_response(controlled_prompt)

    return {
        "normal_prompt": normal_prompt,
        "role_prompt": role_prompt,
        "controlled_prompt": controlled_prompt,
        "normal_response": normal_response,
        "role_response": role_response,
        "controlled_response": controlled_response
    }


if __name__ == "__main__":
    question = input("Enter your question: ")
    role = input("Enter the AI role and instructions: ")
    negative_instruction = input("Enter what the AI should avoid: ")

    try:
        results = evaluate_prompts(
            question,
            role,
            negative_instruction
        )

        print("\n--- NORMAL RESPONSE ---")
        print(results["normal_response"])

        print("\n--- ROLE-BASED RESPONSE ---")
        print(results["role_response"])

        print("\n--- ROLE + NEGATIVE RESPONSE ---")
        print(results["controlled_response"])

    except (OllamaError, ValueError) as error:
        print("Error:", error)
