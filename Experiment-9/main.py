
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:1b"


class OllamaError(Exception):
    pass


def check_connection():
    """Check whether Ollama is running and the model is available."""
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )
        response.raise_for_status()

        models = response.json().get("models", [])
        available = [
            model.get("name", "")
            for model in models
        ]

        if not any(name == MODEL or name.startswith(MODEL + ":")
                   for name in available):
            raise OllamaError(
                f"Model '{MODEL}' was not found. Run: ollama pull {MODEL}"
            )

        return True

    except requests.RequestException as error:
        raise OllamaError(
            "Cannot connect to Ollama. Open Ollama and try again."
        ) from error


def generate_text(prompt):
    """Generate text using the local Ollama model."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            },
            timeout=180
        )
        response.raise_for_status()

        answer = response.json().get("response", "").strip()

        if not answer:
            raise OllamaError("The model returned an empty response.")

        return answer

    except requests.RequestException as error:
        raise OllamaError(
            f"Text generation failed: {error}"
        ) from error


def build_prompt(description, output_format):
    """Create a prompt requesting valid machine-readable data."""

    if output_format == "JSON":
        format_rules = """
Return ONLY one valid JSON object or array.
Do not use Markdown code fences.
Use double quotes around JSON keys and string values.
Use commas correctly.
Do not include comments or explanations.
Do not add trailing commas.
Ensure the result can be parsed by Python's json.loads().
"""

    else:
        format_rules = """
Return ONLY valid YAML.
Do not use Markdown code fences.
Use correct indentation.
Use consistent keys and values.
Do not include explanations outside the YAML.
Ensure the result can be parsed by Python's YAML parser.
"""

    return f"""
You are a structured data generation assistant.

DATASET DESCRIPTION:
{description}

OUTPUT FORMAT:
{output_format}

REQUIREMENTS:
- Follow the dataset description exactly.
- Include all requested fields.
- Use consistent field names and data types.
- Generate realistic example data when values are not specified.
- Return the requested number of records if a number is mentioned.

{format_rules}
"""


def validate_data(text, output_format):
    """Validate generated JSON or YAML using a parser."""

    try:
        if output_format == "JSON":
            parsed = json.loads(text)

        else:
            try:
                import yaml
            except ImportError:
                return {
                    "valid": False,
                    "message": (
                        "PyYAML is not installed. Run: "
                        "pip install pyyaml"
                    ),
                    "data": None
                }

            parsed = yaml.safe_load(text)

        return {
            "valid": True,
            "message": (
                f"Valid {output_format}: the parser accepted the output."
            ),
            "data": parsed
        }

    except (json.JSONDecodeError, ValueError) as error:
        return {
            "valid": False,
            "message": f"Syntax validation failed: {error}",
            "data": None
        }

    except Exception as error:
        return {
            "valid": False,
            "message": f"Validation error: {error}",
            "data": None
        }


def remove_code_fences(text):
    """Remove surrounding Markdown code fences if the model adds them."""
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return text


def run_experiment(description, output_format, max_refinements=2):
    """
    Generate structured data, validate it, and refine the prompt
    if parser validation fails.
    """

    prompt = build_prompt(description, output_format)
    attempts = []
    answer = ""

    for attempt in range(max_refinements + 1):
        answer = generate_text(prompt)
        answer = remove_code_fences(answer)

        validation = validate_data(answer, output_format)

        attempts.append({
            "attempt": attempt + 1,
            "output": answer,
            "valid": validation["valid"],
            "message": validation["message"]
        })

        if validation["valid"]:
            return {
                "output": answer,
                "valid": True,
                "message": validation["message"],
                "attempts": attempts,
                "parsed_data": validation["data"]
            }

        if attempt < max_refinements:
            prompt = f"""
{prompt}

PREVIOUS OUTPUT WAS INVALID.

Previous output:
{answer}

Parser error:
{validation["message"]}

Correct the syntax error and return the COMPLETE corrected
{output_format} output only. Do not include Markdown fences,
comments, or explanations.
"""

    return {
        "output": answer,
        "valid": False,
        "message": attempts[-1]["message"],
        "attempts": attempts,
        "parsed_data": None
    }
