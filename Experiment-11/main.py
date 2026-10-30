
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama


MODEL_NAME = "llama3.2:1b"


class LCELChainError(Exception):
    """Error raised during LCEL chain execution."""
    pass


def build_chain():
    """Build an LCEL chain using prompt, model, and output parser."""

    prompt = ChatPromptTemplate.from_template(
        "Summarize the following text clearly and concisely. "
        "Keep the important information.\n\n"
        "Text: {text}\n\n"
        "Summary:"
    )

    model = ChatOllama(
        model=MODEL_NAME,
        temperature=0.3
    )

    output_parser = StrOutputParser()

    # LCEL chain composition
    chain = prompt | model | output_parser

    return chain


def summarize_text(text):
    """Execute the LCEL chain and return the summary."""

    if not text or not text.strip():
        raise LCELChainError("Please enter some text to summarize.")

    try:
        chain = build_chain()
        result = chain.invoke({"text": text.strip()})

        if not result or not result.strip():
            raise LCELChainError("The model returned an empty response.")

        return result.strip()

    except LCELChainError:
        raise

    except Exception as error:
        raise LCELChainError(
            "Could not execute the LCEL chain. "
            "Check that Ollama is running and the model is installed.\n\n"
            f"Details: {error}"
        ) from error


def check_chain():
    """Verify end-to-end execution with a sample input."""

    test_text = (
        "Artificial Intelligence enables computers to perform tasks "
        "that usually require human intelligence. It is used in "
        "education, healthcare, transportation, and business."
    )

    return summarize_text(test_text)
