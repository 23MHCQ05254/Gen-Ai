
import requests
import re

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:1b"

TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"


class OllamaError(Exception):
    pass


def check_connection():
    """Check that Ollama is running and the model is installed."""
    try:
        response = requests.get(TAGS_URL, timeout=10)
        response.raise_for_status()
        models = response.json().get("models", [])
        names = [m.get("name", "") for m in models]

        if not any(
            name == MODEL_NAME or name.startswith(MODEL_NAME + ":")
            for name in names
        ):
            raise OllamaError(
                f"Model '{MODEL_NAME}' not found. Run:\n"
                f"ollama pull {MODEL_NAME}"
            )

        return True

    except requests.exceptions.ConnectionError:
        raise OllamaError(
            "Ollama is not running. Start Ollama and try again."
        )
    except requests.exceptions.Timeout:
        raise OllamaError("Ollama connection timed out.")
    except requests.exceptions.RequestException as error:
        raise OllamaError(f"Could not connect to Ollama: {error}")


def generate_response(prompt, temperature=0.3):
    """Generate one response from the local Ollama model."""
    if not prompt or not prompt.strip():
        raise OllamaError("The prompt cannot be empty.")

    try:
        response = requests.post(
            GENERATE_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt.strip(),
                "stream": False,
                "options": {"temperature": temperature}
            },
            timeout=300
        )
        response.raise_for_status()

        answer = response.json().get("response", "").strip()

        if not answer:
            raise OllamaError("The model returned an empty response.")

        return answer

    except requests.exceptions.Timeout:
        raise OllamaError(
            "Generation timed out. Please try again."
        )
    except requests.exceptions.ConnectionError:
        raise OllamaError(
            "Lost connection to Ollama. Check that it is running."
        )
    except requests.exceptions.HTTPError as error:
        raise OllamaError(f"Ollama HTTP error: {error}")
    except requests.exceptions.RequestException as error:
        raise OllamaError(f"Request failed: {error}")


def build_round_prompts(prompt_a, prompt_b, prompt_c):
    """Validate and return the three editable prompts."""
    prompts = [
        prompt_a.strip(),
        prompt_b.strip(),
        prompt_c.strip()
    ]

    if not all(prompts):
        raise ValueError("Please fill in all three prompt boxes.")

    return prompts


def count_sentences(text):
    """Estimate the number of sentences in a response."""
    text = re.sub(r"\b(e\.g|i\.e|Mr|Mrs|Dr|Ms)\.", r"\1", text)
    parts = re.split(r"[.!?]+(?:[\"')\]]*)\s*", text.strip())
    return len([part for part in parts if part.strip()])


def check_word_coverage(text, words):
    """Return the percentage of required words or phrases found."""
    if not words:
        return None

    text_lower = text.lower()
    found = sum(1 for word in words if word.lower() in text_lower)
    return round(found / len(words) * 100)


def extract_required_phrases(prompts):
    """Identify likely content requirements from the user's prompts."""
    combined = " ".join(prompts).lower()

    groups = {
        "Setting coverage": [],
        "Theme coverage": [],
        "Key content coverage": []
    }

    known_terms = {
        "Setting coverage": [
            "verona", "italy", "rome", "setting", "place", "location"
        ],
        "Theme coverage": [
            "love", "family conflict", "conflict", "tragedy",
            "friendship", "revenge", "courage", "power", "death"
        ],
        "Key content coverage": [
            "characters", "main character", "ending", "lesson",
            "cause", "effect", "example", "advantages", "disadvantages",
            "steps", "conclusion", "result"
        ]
    }

    for group, candidates in known_terms.items():
        groups[group] = [
            term for term in candidates
            if term in combined
        ]

    # Also extract phrases following common instruction wording.
    match = re.search(
        r"(?:include|mention|cover|discuss|focus on)\s+(.+)",
        combined
    )

    if match and not groups["Key content coverage"]:
        phrase = re.split(r"[.!?\n]", match.group(1))[0]
        items = re.split(r",|\band\b", phrase)
        groups["Key content coverage"] = [
            item.strip(" .:;") for item in items
            if 2 <= len(item.strip()) <= 45
        ][:6]

    return groups


def compare_responses(prompts, responses):
    """
    Produce transparent, rule-based comparisons.

    These are estimates based on text checks, not guaranteed
    assessments of factual accuracy.
    """
    requirements = extract_required_phrases(prompts)
    results = []

    for index, (prompt, response) in enumerate(
        zip(prompts, responses)
    ):
        text = response.strip()
        words = re.findall(r"\b[\w'-]+\b", text)
        sentence_count = count_sentences(text)
        word_count = len(words)

        # Check length compliance when a numeric length is requested.
        requested_sentences = None
        match = re.search(
            r"\b(?:exactly\s+)?(\d+)\s+sentences?\b",
            prompt.lower()
        )
        if match:
            requested_sentences = int(match.group(1))

        if requested_sentences:
            length_score = 100 if sentence_count == requested_sentences else max(
                0, 100 - abs(sentence_count - requested_sentences) * 35
            )
            length_note = (
                f"{sentence_count} sentence(s); "
                f"{requested_sentences} requested"
            )
        else:
            length_score = min(100, word_count * 2)
            length_note = f"{sentence_count} sentence(s), {word_count} words"

        # Simple readability proxy: average words per sentence.
        avg_sentence_length = (
            word_count / sentence_count if sentence_count else word_count
        )
        if word_count == 0:
            style_score = 0
        elif avg_sentence_length <= 22:
            style_score = 90
        elif avg_sentence_length <= 30:
            style_score = 75
        else:
            style_score = 60

        # Prompt-specific keyword coverage.
        all_terms = []
        for terms in requirements.values():
            all_terms.extend(terms)

        all_terms = list(dict.fromkeys(all_terms))
        content_score = check_word_coverage(text, all_terms)

        # Relevance proxy: overlap between meaningful prompt words
        # and response words.
        ignored = {
            "the", "and", "for", "with", "that", "this", "from",
            "into", "your", "using", "about", "what", "when",
            "where", "write", "explain", "include", "mention",
            "summarize", "summary", "response", "answer", "please",
            "simple", "clear", "exactly", "sentences", "sentence"
        }

        prompt_words = {
            word.lower()
            for word in re.findall(r"\b[a-zA-Z]{3,}\b", prompt)
            if word.lower() not in ignored
        }
        response_words = {
            word.lower()
            for word in re.findall(r"\b[a-zA-Z]{3,}\b", text)
        }

        relevance_score = (
            round(
                len(prompt_words & response_words)
                / len(prompt_words) * 100
            )
            if prompt_words else 0
        )

        scores = {
            "Length compliance": length_score,
            "Style and readability": style_score,
            "Prompt relevance": relevance_score,
        }

        if content_score is not None:
            scores["Key content coverage"] = content_score

        overall = round(sum(scores.values()) / len(scores))

        results.append({
            "round": index + 1,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "length_note": length_note,
            "scores": scores,
            "overall": overall
        })

    return results, requirements
