
import requests

BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:1b"


class OllamaError(Exception):
    pass


def check_connection():
    try:
        response = requests.get(f"{BASE_URL}/api/tags", timeout=10)
        response.raise_for_status()

        models = response.json().get("models", [])
        installed = [m.get("name", "") for m in models]

        if not any(
            name == MODEL_NAME or name.startswith(MODEL_NAME + ":")
            for name in installed
        ):
            raise OllamaError(
                "Model not found. Run: ollama pull llama3.2:1b"
            )

        return True

    except requests.RequestException as exc:
        raise OllamaError(
            "Cannot connect to Ollama. Please start Ollama."
        ) from exc


def generate_response(prompt, temperature=0.3):
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature}
            },
            timeout=300
        )
        response.raise_for_status()

        answer = response.json().get("response", "").strip()

        if not answer:
            raise OllamaError("The AI returned an empty response.")

        return answer

    except requests.Timeout as exc:
        raise OllamaError(
            "The AI took too long to respond. Please try again."
        ) from exc
    except requests.RequestException as exc:
        raise OllamaError(f"Ollama error: {exc}") from exc


def diagnose_and_refine(original_prompt):
    instruction = f"""
You are an expert prompt-debugging assistant.

Analyze the user's prompt and improve it.

USER PROMPT:
\"\"\"
{original_prompt}
\"\"\"

Identify all applicable problems:
1. Ambiguity or vague wording.
2. Missing context or information.
3. Contradictory instructions.
4. Missing output format or length requirements.
5. Missing examples or other useful constraints.

Do not invent problems if the prompt is already clear.
Explain the actual problems found. If no major problem exists, say so.
Then write a corrected prompt that preserves the user's original intention.
Add only useful clarifications. Resolve contradictions and specify a
suitable output format when necessary.

Use this exact output structure:

ERROR ANALYSIS:
- Error: [problem found, or No major error detected]
- Cause: [why it is a problem]
- Impact: [how it may affect the AI response]
- Fix: [how to correct it]

Repeat the four lines for each applicable problem.

CORRECTED PROMPT:
Write the complete improved prompt here.

Do not generate the answer to the user's task in this step.
"""

    return generate_response(instruction, temperature=0.2)


def extract_corrected_prompt(analysis):
    marker = "CORRECTED PROMPT:"

    if marker.lower() in analysis.lower():
        start = analysis.lower().find(marker.lower()) + len(marker)
        corrected = analysis[start:].strip()

        for end_marker in ["\nERROR ANALYSIS:", "\nEXPLANATION:"]:
            position = corrected.lower().find(end_marker.lower())
            if position >= 0:
                corrected = corrected[:position].strip()

        return corrected.strip().strip('"')

    return ""


def compare_responses(original, corrected):
    return {
        "Original word count": len(original.split()),
        "Corrected word count": len(corrected.split()),
        "Original response generated": bool(original.strip()),
        "Corrected response generated": bool(corrected.strip()),
        "Response changed": original.strip() != corrected.strip()
    }
