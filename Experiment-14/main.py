
import re
from ollama import chat

MODEL = "llama3.2:1b"


def calculator(operation: str, a: float, b: float) -> str:
    """Registered Python calculator tool."""

    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return "Cannot divide by zero."
        result = a / b
    else:
        return "Unsupported operation."

    return str(int(result) if result.is_integer() else result)


def detect_calculation(question: str):
    """Detect common arithmetic questions."""

    q = question.lower().replace(",", "")
    number = r"(-?\d+(?:\.\d+)?)"

    patterns = [
        (r"(?:" + r"calculate\s+)?" + number +
         r"\s*(?:multiplied by|multiply by|times|x|\*)\s*" +
         number, "multiply"),

        (r"(?:" + r"calculate\s+)?" + number +
         r"\s*(?:divided by|divide by|over|/)\s*" +
         number, "divide"),

        (r"(?:" + r"calculate\s+)?" + number +
         r"\s*(?:plus|\+)\s*" + number, "add"),

        (r"(?:" + r"calculate\s+)?" + number +
         r"\s*(?:minus|-)\s*" + number, "subtract"),

        (r"(?:multiply|multiply the numbers)\s+" +
         number + r"\s+(?:by|and)\s+" + number, "multiply"),

        (r"(?:add)\s+" + number + r"\s+(?:and|to)\s+" +
         number, "add"),

        (r"(?:subtract)\s+" + number + r"\s+(?:from)\s+" +
         number, "subtract"),

        (r"(?:" + r"what is\s+)?" + number +
         r"\s+multiplied by\s+" + number, "multiply"),

        (r"(?:" + r"what is\s+)?" + number +
         r"\s+divided by\s+" + number, "divide"),
    ]

    for pattern, operation in patterns:
        match = re.search(pattern, q)
        if match:
            a, b = map(float, match.groups())
            return operation, a, b

    # Handle requests such as "Calculate 125 multiplied by 24"
    match = re.search(
        r"calculate\s+" + number +
        r"\s+(multiplied by|divided by|plus|minus)\s+" +
        number,
        q,
    )

    if match:
        a = float(match.group(1))
        operator = match.group(2)
        b = float(match.group(3))

        operations = {
            "multiplied by": "multiply",
            "divided by": "divide",
            "plus": "add",
            "minus": "subtract",
        }
        return operations[operator], a, b

    return None


def run_agent(question: str) -> dict:
    """Run the agent and return only the final answer to the UI."""

    if not question.strip():
        raise ValueError("Please enter a question.")

    calculation = detect_calculation(question)

    if calculation:
        operation, a, b = calculation

        # Execute the registered calculator function.
        result = calculator(operation, a, b)

        return {
            "answer": result,
            "tool_used": True,
            "tool_log": [],
        }

    # Send non-calculation questions to Ollama.
    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "Answer questions clearly and simply."
                ),
            },
            {"role": "user", "content": question},
        ],
        options={"temperature": 0},
    )

    return {
        "answer": response.message.content or "No answer generated.",
        "tool_used": False,
        "tool_log": [],
    }
