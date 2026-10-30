
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.messages import SystemMessage, HumanMessage

EMBEDDING_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.2:1b"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


class PDFRAGError(Exception):
    pass


def load_pdf(pdf_file):
    """Extract text from an uploaded PDF file."""
    try:
        reader = PdfReader(pdf_file)
        documents = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if text.strip():
                documents.append(
                    Document(
                        page_content=text.strip(),
                        metadata={
                            "source": pdf_file.name,
                            "page": page_number
                        }
                    )
                )

        if not documents:
            raise PDFRAGError(
                "No readable text was found. "
                "The PDF may contain scanned images."
            )

        return documents

    except PDFRAGError:
        raise
    except Exception as error:
        raise PDFRAGError(
            f"Could not read the PDF: {error}"
        ) from error


def split_documents(documents):
    """Split extracted page text into overlapping chunks."""
    chunks = []

    for document in documents:
        text = document.page_content
        start = 0

        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    Document(
                        page_content=chunk_text,
                        metadata={
                            **document.metadata,
                            "chunk_id": len(chunks) + 1
                        }
                    )
                )

            if end >= len(text):
                break

            start = end - CHUNK_OVERLAP

    if not chunks:
        raise PDFRAGError("No chunks were created from this PDF.")

    return chunks


def create_vector_store(chunks):
    """Generate embeddings and store chunks in memory."""
    try:
        embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL
        )

        vector_store = InMemoryVectorStore(
            embedding=embeddings
        )

        vector_store.add_documents(chunks)

        # Verify that indexed text can be retrieved.
        results = vector_store.similarity_search(
            chunks[0].page_content[:150],
            k=1
        )

        if not results:
            raise PDFRAGError(
                "The consistency check could not retrieve a chunk."
            )

        return vector_store

    except PDFRAGError:
        raise
    except Exception as error:
        raise PDFRAGError(
            "Embedding or indexing failed. Make sure Ollama is "
            "running and nomic-embed-text is installed.\n\n"
            f"Details: {error}"
        ) from error


def answer_question(vector_store, question, top_k=4):
    """Retrieve relevant chunks and answer using their contents."""
    if not question or not question.strip():
        raise PDFRAGError("Please enter a question.")

    try:
        retrieved_docs = vector_store.similarity_search(
            question.strip(),
            k=top_k
        )

        if not retrieved_docs:
            raise PDFRAGError("No relevant document content was found.")

        context_parts = []

        for doc in retrieved_docs:
            page = doc.metadata.get("page", "?")
            context_parts.append(
                f"[PDF page {page}]\n{doc.page_content}"
            )

        context = "\n\n".join(context_parts)

        model = ChatOllama(
            model=CHAT_MODEL,
            temperature=0
        )

        messages = [
            SystemMessage(
                content=(
                    "You are a PDF question-answering assistant. "
                    "Answer using only the supplied PDF context. "
                    "Be clear and helpful. If the context does not "
                    "contain enough information to answer, say that "
                    "the answer could not be found in the relevant "
                    "PDF content. Do not invent facts. "
                    "Mention page numbers when useful."
                )
            ),
            HumanMessage(
                content=(
                    f"PDF CONTEXT:\n{context}\n\n"
                    f"USER QUESTION:\n{question.strip()}\n\n"
                    "Answer the question using the PDF context."
                )
            )
        ]

        response = model.invoke(messages)
        answer = response.content

        if isinstance(answer, list):
            answer = "\n".join(
                str(item.get("text", item))
                if isinstance(item, dict) else str(item)
                for item in answer
            )

        answer = str(answer).strip()

        if not answer:
            raise PDFRAGError("The model returned an empty answer.")

        return answer, retrieved_docs

    except PDFRAGError:
        raise
    except Exception as error:
        raise PDFRAGError(
            "Could not generate an answer. Check that Ollama is "
            "running and llama3.2:1b is installed.\n\n"
            f"Details: {error}"
        ) from error


def inspect_index(documents, chunks, vector_store):
    """Perform basic indexing consistency checks."""
    checks = {
        "PDF text extracted": len(documents) > 0,
        "Chunks created": len(chunks) > 0,
        "All chunks contain text": all(
            chunk.page_content.strip() for chunk in chunks
        ),
        "All chunks have page numbers": all(
            "page" in chunk.metadata for chunk in chunks
        ),
        "All chunks have unique IDs": len({
            chunk.metadata["chunk_id"] for chunk in chunks
        }) == len(chunks),
        "Vector retrieval works": bool(
            vector_store.similarity_search(
                chunks[0].page_content[:150], k=1
            )
        )
    }

    return checks
