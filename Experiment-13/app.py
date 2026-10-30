
import os
import tempfile
import streamlit as st

from main import (
    load_and_split_pdf,
    build_vector_store,
    answer_with_retrieval,
)

# -------------------- PAGE SETTINGS --------------------

st.set_page_config(
    page_title="RAG Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------- SESSION STATE --------------------

defaults = {
    "vector_store": None,
    "index_ready": False,
    "document_name": "",
    "rag_answer": "",
    "rag_error": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------- CUSTOM DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background: #101A2B;
    color: #F1F5F9;
}

.block-container {
    max-width: 1450px;
    padding-top: 0.35rem;
    padding-bottom: 0.8rem;
}

h1, h2, h3, p, label {
    color: #F1F5F9;
}

.hero {
    padding: 15px 22px;
    border: 1px solid #356B70;
    border-radius: 13px;
    background: linear-gradient(115deg, #20384F, #175B59);
    margin-bottom: 5px;
}

.hero h1 {
    margin: 0;
    padding: 0;
    font-size: 1.9rem;
    color: white;
}

.hero p {
    margin: 4px 0 0 0;
    color: #D1E7E8;
    font-size: 0.92rem;
}

.section-head {
    font-size: 1.08rem;
    font-weight: 700;
    color: #7DE3D1;
    margin: 7px 0 3px 0;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.45rem;
}

div[data-testid="stFileUploader"] {
    background: #19283D;
    border: 1px dashed #4D8290;
    border-radius: 9px;
    padding: 7px;
}

div[data-testid="stFileUploader"] section {
    background: #19283D;
}

div[data-testid="stFileUploader"] button {
    background: #176B65 !important;
    color: white !important;
    border: 1px solid #42B8A8 !important;
    border-radius: 7px !important;
}

.stButton > button {
    background: #176B65;
    color: white;
    border: 1px solid #42B8A8;
    border-radius: 8px;
    font-weight: 600;
    min-height: 39px;
}

.stButton > button:hover {
    background: #21877D;
    color: white;
    border-color: #7DE3D1;
}

.stTextArea textarea {
    background: #101A2B;
    color: #F1F5F9;
    border: 1px solid #405875;
    border-radius: 8px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #30445E;
    border-radius: 11px;
    background: #142238;
}

.answer-card {
    background: #19283D;
    border: 1px solid #30445E;
    border-radius: 11px;
    padding: 16px;
    min-height: 180px;
    overflow-wrap: anywhere;
}

.answer-card h3 {
    color: #7DE3D1;
    font-size: 1.08rem;
    margin-top: 0;
}

.answer-content {
    color: #E2E8F0;
    font-size: 0.95rem;
    line-height: 1.65;
    overflow-wrap: anywhere;
}

.status {
    background: #123D3B;
    border: 1px solid #287C70;
    color: #A7F3D0;
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 0.9rem;
}

hr {
    border-color: #30445E;
    margin: 6px 0;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------

st.markdown("""
<div class="hero">
    <h1>Ask. Retrieve. Compare.</h1>
    <p>Ask questions and get answers grounded in your PDF document.</p>
</div>
""", unsafe_allow_html=True)

# -------------------- SECTION 1: KNOWLEDGE SOURCE --------------------

st.markdown(
    '<div class="section-head">01 &nbsp; Knowledge Source</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    uploaded_file = st.file_uploader(
        "Upload your PDF document",
        type=["pdf"],
        key="pdf_upload",
    )

    c1, c2 = st.columns([1, 2], gap="small")

    with c1:
        build_clicked = st.button(
            "Build Knowledge Index",
            use_container_width=True,
        )

    with c2:
        if st.session_state.index_ready:
            st.markdown(
                f'<div class="status">✓ Index ready: '
                f'{st.session_state.document_name}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.caption(
                "Upload a PDF and build the index before asking questions."
            )

if build_clicked:
    if uploaded_file is None:
        st.warning("Please upload a PDF document first.")
    else:
        temp_path = None

        try:
            with st.spinner("Building knowledge index..."):
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf",
                ) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_path = temp_file.name

                chunks = load_and_split_pdf(temp_path)

                if not chunks:
                    raise ValueError(
                        "No readable text was found in the PDF."
                    )

                new_vector_store = build_vector_store(chunks)

                if new_vector_store is None:
                    raise ValueError(
                        "The vector store was not created successfully."
                    )

                st.session_state.vector_store = new_vector_store
                st.session_state.index_ready = True
                st.session_state.document_name = uploaded_file.name
                st.session_state.rag_answer = ""
                st.session_state.rag_error = ""

        except Exception as e:
            st.session_state.vector_store = None
            st.session_state.index_ready = False
            st.session_state.rag_error = (
                f"{type(e).__name__}: {e}"
            )
            st.error(f"Index creation failed: {e}")

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

# -------------------- SECTION 2: QUESTION WORKSPACE --------------------

st.markdown(
    '<div class="section-head">02 &nbsp; Question Workspace</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    question = st.text_area(
        "Enter your question",
        placeholder="Example: What are the attendance requirements?",
        height=90,
        key="question_input",
    )

    c1, c2 = st.columns(2, gap="small")

    with c1:
        run_clicked = st.button(
            "Generate Answer",
            use_container_width=True,
        )

    with c2:
        clear_clicked = st.button(
            "Clear Answers",
            use_container_width=True,
        )

if clear_clicked:
    st.session_state.rag_answer = ""
    st.session_state.rag_error = ""
    st.rerun()

# -------------------- GENERATE RAG ANSWER --------------------

if run_clicked:
    if not question.strip():
        st.warning("Please enter a question.")

    elif not st.session_state.index_ready:
        st.warning("Please upload a PDF and build the knowledge index first.")

    else:
        st.session_state.rag_answer = ""
        st.session_state.rag_error = ""

        try:
            with st.spinner("Generating answer..."):
                result = answer_with_retrieval(
                    st.session_state.vector_store,
                    question.strip(),
                )

                if result is None:
                    raise ValueError("The model returned no answer.")

                result = getattr(result, "content", result)
                result = str(result).strip()

                if not result:
                    raise ValueError("The model returned an empty answer.")

                st.session_state.rag_answer = result

        except Exception as e:
            st.session_state.rag_error = (
                f"{type(e).__name__}: {e}"
            )

# -------------------- SECTION 3: ANSWER --------------------

st.markdown(
    '<div class="section-head">03 &nbsp; Generated Answer</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.answer-title) {
        background: #19283D;
        border: 1px solid #30445E;
        border-radius: 11px;
        padding: 16px;
    }

    .answer-title {
        color: #7DE3D1;
        font-size: 1.08rem;
        font-weight: 700;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown(
        '<div class="answer-title">RAG-Enhanced Answer</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.rag_answer:
        st.markdown(st.session_state.rag_answer)
    elif st.session_state.rag_error:
        st.error(st.session_state.rag_error)
    else:
        st.caption(
            "Your answer based on the uploaded PDF will appear here."
        )
