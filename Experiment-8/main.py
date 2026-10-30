
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
            f"{BASE_URL}/api/tags", timeout=10
        )
        response.raise_for_status()

        models = response.json().get("models", [])
        available = [
            model.get("name", "") for model in models
        ]

        if not any(
            name == MODEL_NAME or name.startswith(MODEL_NAME + ":")
            for name in available
        ):
            raise OllamaError(
                f"Model '{MODEL_NAME}' is not installed. "
                f"Run: ollama pull {MODEL_NAME}"
            )

        return True

    except requests.RequestException as exc:
        raise OllamaError(
            "Cannot connect to Ollama. Make sure Ollama is running."
        ) from exc


def generate_text(prompt):
    """Generate text using the local Ollama model."""
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3}
            },
            timeout=TIMEOUT
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()

        if not answer:
            raise OllamaError("The model returned an empty response.")

        return answer

    except requests.RequestException as exc:
        raise OllamaError(
            f"Text generation failed: {exc}"
        ) from exc


def build_prompt(topic, output_format, count):
    """Create a prompt for the selected output structure."""

    instructions = {
        "Bullet List": (
            f"Write exactly {count} bullet points using '- '."
        ),
        "Numbered List": (
            f"Write exactly {count} numbered points using 1., 2., 3., etc."
        ),
        "Markdown Table": (
            "Return a Markdown table with exactly these columns: "
            "'Item' and 'Description'. "
            f"Include exactly {count} data rows, excluding the header."
        ),
        "Headings and Points": (
            "Use a clear Markdown heading followed by bullet points. "
            f"Include exactly {count} bullet points."
        )
    }

    return f"""
You are an educational assistant helping a B.Tech student.

Topic: {topic}

Required output format: {output_format}

Instructions:
- Explain the topic in simple English.
- Keep the answer relevant and easy to understand.
- {instructions[output_format]}
- Follow the requested format carefully.
- Do not add an introduction or conclusion outside the format.
- Return only the requested answer.
"""


def verify_structure(answer, output_format, count):
    """Check basic formatting rules in the generated answer."""
    lines = [
        line.strip()
        for line in answer.splitlines()
        if line.strip()
    ]

    bullet_lines = [
        line for line in lines
        if line.startswith(("- ", "* ", "• "))
    ]

    numbered_lines = [
        line for line in lines
        if __import__("re").match(r"^\d+[\.\)]\s+", line)
    ]

    table_lines = [
        line for line in lines
        if line.startswith("|") and line.endswith("|")
    ]

    markdown_heading = any(
        line.startswith("#") for line in lines
    )

    checks = {}

    if output_format == "Bullet List":
        checks["Correct bullet count"] = len(bullet_lines) == count
        checks["Bullet formatting present"] = len(bullet_lines) > 0

    elif output_format == "Numbered List":
        checks["Correct numbered item count"] = (
            len(numbered_lines) == count
        )
        checks["Numbered formatting present"] = (
            len(numbered_lines) > 0
        )

    elif output_format == "Markdown Table":
        checks["Markdown table present"] = len(table_lines) >= 3

        if len(table_lines) >= 2:
            header = table_lines[0].lower()
            checks["Expected columns present"] = (
                "item" in header and "description" in header
            )
            checks["Correct data row count"] = (
                len(table_lines) - 2 == count
            )
        else:
            checks["Expected columns present"] = False
            checks["Correct data row count"] = False

    elif output_format == "Headings and Points":
        checks["Markdown heading present"] = markdown_heading
        checks["Correct bullet count"] = len(bullet_lines) == count

    passed = all(checks.values()) if checks else False

    return {
        "checks": checks,
        "passed": passed,
        "bullet_count": len(bullet_lines),
        "numbered_count": len(numbered_lines),
        "table_line_count": len(table_lines)
    }


def run_experiment(topic, output_format, count=3):
    """Generate structured output and verify its format."""
    if not topic.strip():
        raise ValueError("Please enter a topic.")

    prompt = build_prompt(topic, output_format, count)
    answer = generate_text(prompt)
    verification = verify_structure(
        answer, output_format, count
    )

    return {
        "topic": topic,
        "format": output_format,
        "prompt": prompt,
        "answer": answer,
        "verification": verification
    }


if __name__ == "__main__":
    check_connection()

    topic = input("Enter a topic: ")
    result = run_experiment(
        topic,
        "Markdown Table",
        3
    )

    print("\nGenerated Answer:\n")
    print(result["answer"])

    print("\nStructure Verification:\n")
    for check, passed in result["verification"]["checks"].items():
        print(f"{check}: {'PASS' if passed else 'FAIL'}")
