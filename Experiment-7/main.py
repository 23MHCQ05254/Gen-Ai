
import requests
import re

BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:1b"
TIMEOUT = 300


class OllamaError(Exception):
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
            model.get("name", "").split(":")[0]
            == MODEL_NAME.split(":")[0]
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


def generate_text(prompt):
    """Generate text using the local Ollama model."""
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
            f"Text generation failed: {error}"
        ) from error


def word_count(text):
    return len(re.findall(r"\b[\w'-]+\b", text))


def bullet_count(text):
    return sum(
        1 for line in text.splitlines()
        if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line)
    )


def run_refinement(topic, source_text=""):
    """
    Generate an initial response, refine it using constraints,
    and perform a second refinement for clarity and completeness.
    """

    topic = topic.strip() or "General topic"
    source_text = source_text.strip()

    source_section = ""

    if source_text:
        source_section = f"""
Use the following source text as the main reference.
Do not invent facts that contradict it.

SOURCE TEXT:
{source_text}
"""

    # Stage 1: Initial response
    initial_prompt = f"""
You are a helpful educational assistant.

Write an initial explanation of the topic: {topic}

Requirements:
- Use simple English.
- Explain the main idea clearly.
- Include useful information.
- Make the response understandable for a college student.
- Do not force a fixed word count or bullet count at this stage.

{source_section}

Return only the response.
"""

    initial_response = generate_text(initial_prompt)

    # Stage 2: Apply explicit constraints
    refinement_1_prompt = f"""
You are refining an earlier answer for a college student.

TOPIC:
{topic}

ORIGINAL RESPONSE:
{initial_response}

{source_section}

Rewrite the response using these constraints:
1. Write between 80 and 120 words.
2. Include exactly 5 bullet points.
3. Use simple, clear English.
4. Keep the information relevant to the topic.
5. Avoid unnecessary repetition.
6. Do not add an introduction or conclusion outside the 5 bullet points.
7. Check the word count and bullet count before returning the answer.

Return only the refined response.
"""

    refinement_1_response = generate_text(refinement_1_prompt)

    # Stage 3: Iterative refinement
    refinement_2_prompt = f"""
You are performing a second refinement of an educational answer.

TOPIC:
{topic}

PREVIOUS REFINED RESPONSE:
{refinement_1_response}

{source_section}

Improve the previous response using all these constraints:
1. Write between 80 and 120 words.
2. Include exactly 5 bullet points.
3. Use simple English that is easy to understand and memorize.
4. Include a clear definition or explanation of the topic.
5. Include at least one relevant example.
6. Avoid repeating complete sentences from the previous response.
7. Preserve correct and relevant information.
8. Do not add an introduction or conclusion outside the 5 bullet points.
9. Check the word count and bullet count before returning the answer.

Return only the final refined response.
"""

    refinement_2_response = generate_text(refinement_2_prompt)

    return {
        "initial_response": initial_response,
        "refinement_1_response": refinement_1_response,
        "refinement_2_response": refinement_2_response,
        "initial_prompt": initial_prompt.strip(),
        "refinement_1_prompt": refinement_1_prompt.strip(),
        "refinement_2_prompt": refinement_2_prompt.strip(),
    }


if __name__ == "__main__":
    try:
        topic = input("Enter the topic: ")
        source_text = input(
            "Enter optional source text (or press Enter to skip): "
        )

        check_connection()

        results = run_refinement(topic, source_text)

        print("\n--- INITIAL RESPONSE ---")
        print(results["initial_response"])

        print("\n--- REFINEMENT 1 ---")
        print(results["refinement_1_response"])
        print("Word count:", word_count(results["refinement_1_response"]))
        print("Bullet count:", bullet_count(results["refinement_1_response"]))

        print("\n--- REFINEMENT 2 ---")
        print(results["refinement_2_response"])
        print("Word count:", word_count(results["refinement_2_response"]))
        print("Bullet count:", bullet_count(results["refinement_2_response"]))

    except (OllamaError, ValueError) as error:
        print("Error:", error)
