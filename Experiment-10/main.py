
import requests
import re

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:1b"


class OllamaError(Exception):
    pass


def check_connection():
    try:
        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=5
        )
        response.raise_for_status()

        models = response.json().get("models", [])
        model_names = [item.get("name", "") for item in models]

        if not any(name.split(":")[0] == MODEL.split(":")[0]
                   for name in model_names):
            raise OllamaError(
                f"Model {MODEL} not found. Run: ollama pull {MODEL}"
            )

        return True

    except requests.RequestException as error:
        raise OllamaError(
            "Cannot connect to Ollama. Open Ollama and try again."
        ) from error


def generate_text(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 400
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
            raise OllamaError("The model returned an empty response.")

        return answer

    except requests.RequestException as error:
        raise OllamaError(
            f"Failed to generate a response: {error}"
        ) from error


def clean_answer(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()


def direct_answer(problem):
    prompt = f"""
Solve this problem directly.
Give the final answer and a brief explanation.
Do not invent facts.

Problem:
{problem}

Format:
Final Answer: ...
"""
    return clean_answer(generate_text(prompt))


def chain_of_thought_answer(problem):
    prompt = f"""
Solve this problem carefully.
Give a brief numbered explanation of the important steps,
followed by a clear final answer. Do not provide a lengthy
internal monologue. If information is insufficient, say so.

Problem:
{problem}

Format:
Steps:
1. ...
2. ...

Final Answer: ...
"""
    return clean_answer(generate_text(prompt))


def decompose_problem(problem):
    # Step 1: Create three sub-questions
    planning_prompt = f"""
Break the problem into exactly three small, sequential questions.
Each question should help solve the original problem.
Do not solve the problem yet.

Problem:
{problem}

Return only a numbered list of three questions.
"""

    questions_text = clean_answer(generate_text(planning_prompt))

    questions = []
    for line in questions_text.splitlines():
        match = re.match(r"^\s*(?:\d+[\.\)]|[-*])\s+(.+)", line)
        if match:
            questions.append(match.group(1).strip())

    if len(questions) < 3:
        questions = [
            "What facts are given in the problem?",
            "What relationship or rule connects those facts?",
            "What conclusion follows from those facts?"
        ]

    questions = questions[:3]
    partial_answers = []

    # Step 2: Answer each sub-question sequentially
    for index, question in enumerate(questions, start=1):
        previous_parts = []

        for item in partial_answers:
            previous_parts.append(
                "Question: " + item["question"] +
                "\nAnswer: " + item["answer"]
            )

        previous = "\n".join(previous_parts)
        if not previous:
            previous = "None yet."

        sub_prompt = f"""
Solve this sub-question using the original problem and any
earlier partial answers. Be brief and do not invent facts.

Original problem:
{problem}

Current sub-question:
{question}

Earlier partial answers:
{previous}

Give only the answer to the current sub-question.
"""

        answer = clean_answer(generate_text(sub_prompt))

        partial_answers.append({
            "number": index,
            "question": question,
            "answer": answer
        })

    # Step 3: Combine answers without nested f-string expressions
    combined_parts = []

    for item in partial_answers:
        part = (
            str(item["number"]) + ". " + item["question"] +
            "\nAnswer: " + item["answer"]
        )
        combined_parts.append(part)

    combined_text = "\n".join(combined_parts)

    combined_prompt = f"""
Use the partial answers to solve the original problem.
Do not add unsupported facts.

Original problem:
{problem}

Partial answers:
{combined_text}

Provide a concise conclusion.

Format:
Final Answer: ...
"""

    final_answer = clean_answer(generate_text(combined_prompt))

    return {
        "questions": questions,
        "partial_answers": partial_answers,
        "final_answer": final_answer
    }


def compare_answers(direct, cot, decomposed, expected_answer=""):
    if not expected_answer.strip():
        return {
            "expected_answer": "",
            "direct_match": None,
            "cot_match": None,
            "decomposed_match": None,
            "message": (
                "Enter an expected answer to compare automatically. "
                "Otherwise, compare the answers manually."
            )
        }

    expected = " ".join(
        re.sub(r"[^a-z0-9\s]", " ", expected_answer.lower()).split()
    )

    def matches(answer):
        normalized = " ".join(
            re.sub(r"[^a-z0-9\s]", " ", answer.lower()).split()
        )
        return expected in normalized

    direct_match = matches(direct)
    cot_match = matches(cot)
    decomposed_match = matches(decomposed)

    return {
        "expected_answer": expected_answer,
        "direct_match": direct_match,
        "cot_match": cot_match,
        "decomposed_match": decomposed_match,
        "message": (
            "This comparison checks for an exact expected-answer text "
            "match. It is not a complete semantic accuracy measurement."
        )
    }


def run_experiment(problem, expected_answer=""):
    check_connection()

    direct = direct_answer(problem)
    cot = chain_of_thought_answer(problem)
    decomposition = decompose_problem(problem)

    comparison = compare_answers(
        direct,
        cot,
        decomposition["final_answer"],
        expected_answer
    )

    return {
        "direct": direct,
        "cot": cot,
        "decomposition": decomposition,
        "comparison": comparison
    }
