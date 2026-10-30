
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama


# -------------------- MODEL SETTINGS --------------------

CHAT_MODEL = "llama3.2:1b"
EMBEDDING_MODEL = "nomic-embed-text"


# -------------------- LOAD AND SPLIT PDF --------------------

def load_and_split_pdf(pdf_path):
    """
    Load a PDF and split it into a flat list of LangChain Documents.
    """

    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        if not documents:
            raise ValueError("The PDF contains no readable pages.")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
        )

        chunks = splitter.split_documents(documents)

        # Remove empty chunks and ensure each item is a Document.
        chunks = [
            chunk
            for chunk in chunks
            if hasattr(chunk, "page_content")
            and chunk.page_content.strip()
        ]

        if not chunks:
            raise ValueError(
                "No readable text was found. "
                "The PDF may be scanned or image-only."
            )

        return chunks

    except Exception as e:
        raise RuntimeError(
            f"Could not load or split the PDF: {e}"
        ) from e


# -------------------- CREATE VECTOR INDEX --------------------

def build_vector_store(chunks):
    """
    Convert Document chunks into embeddings and store them in FAISS.
    """

    try:
        # Accept either a list of Documents or a nested list.
        flat_chunks = []

        def flatten(items):
            for item in items:
                if isinstance(item, (list, tuple)):
                    flatten(item)
                else:
                    flat_chunks.append(item)

        flatten(chunks)

        # Keep only actual LangChain Document-like objects.
        valid_chunks = [
            item
            for item in flat_chunks
            if hasattr(item, "page_content")
            and isinstance(item.page_content, str)
            and item.page_content.strip()
        ]

        if not valid_chunks:
            raise ValueError(
                "No valid document chunks were supplied to FAISS."
            )

        embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL
        )

        vector_store = FAISS.from_documents(
            documents=valid_chunks,
            embedding=embeddings,
        )

        return vector_store

    except Exception as e:
        raise RuntimeError(
            f"Could not create embeddings or the vector index. "
            f"Check Ollama and the embedding model. Details: {e}"
        ) from e


# -------------------- RETRIEVE RELEVANT CHUNKS --------------------

def retrieve_chunks(vector_store, question, top_k=3):
    """
    Retrieve the most relevant document chunks for a question.
    """

    if vector_store is None:
        raise ValueError("The knowledge index has not been built.")

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    documents = vector_store.similarity_search(
        question.strip(),
        k=top_k,
    )

    return documents


# -------------------- NORMAL AI ANSWER --------------------

def answer_without_retrieval(question):
    """
    Answer using the language model without PDF context.
    """

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    try:
        llm = ChatOllama(
            model=CHAT_MODEL,
            temperature=0.2,
        )

        response = llm.invoke(
            "Answer the following question clearly and simply. "
            "Do not claim to have read any uploaded document.\n\n"
            f"Question: {question.strip()}"
        )

        answer = getattr(response, "content", response)

        if not answer or not str(answer).strip():
            raise ValueError("The model returned an empty answer.")

        return str(answer).strip()

    except Exception as e:
        raise RuntimeError(
            f"Normal AI failed. Check that Ollama is running "
            f"and model '{CHAT_MODEL}' is installed. Details: {e}"
        ) from e


# -------------------- RAG-ENHANCED ANSWER --------------------

def answer_with_retrieval(vector_store, question, top_k=3):
    """
    Retrieve relevant PDF chunks and use them as context for the answer.
    """

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    try:
        # Retrieve relevant passages from the indexed PDF.
        documents = retrieve_chunks(
            vector_store,
            question.strip(),
            top_k=top_k,
        )

        if not documents:
            return (
                "No relevant information was found in the indexed PDF. "
                "Try asking a different question."
            )

        # Build context from Document objects.
        context_parts = []

        for doc in documents:
            if hasattr(doc, "page_content"):
                text = doc.page_content.strip()

                if text:
                    page = doc.metadata.get("page", None)
                    if page is not None:
                        context_parts.append(
                            f"Page {int(page) + 1}:\n{text}"
                        )
                    else:
                        context_parts.append(text)

        context = "\n\n".join(context_parts)

        if not context.strip():
            return "No readable text was retrieved from the PDF."

        # Generate an answer grounded in retrieved context.
        llm = ChatOllama(
            model=CHAT_MODEL,
            temperature=0.1,
        )

        prompt = f"""
You are an assistant answering questions using a supplied document.

Instructions:
1. Use the document context below to answer the question.
2. Do not invent rules, dates, numbers, or facts.
3. If the answer is not available in the context, clearly say:
   "The uploaded document does not provide enough information
   to answer this question."
4. Explain the answer in simple, clear English.
5. Keep the answer relevant to the question.

DOCUMENT CONTEXT:
{context}

QUESTION:
{question.strip()}

ANSWER:
"""

        response = llm.invoke(prompt)
        answer = getattr(response, "content", response)

        if not answer or not str(answer).strip():
            raise ValueError("The RAG model returned an empty answer.")

        return str(answer).strip()

    except Exception as e:
        raise RuntimeError(
            f"RAG answer generation failed: {e}"
        ) from e
