
import streamlit as st
import html

from main import (
    load_pdf,
    split_documents,
    create_vector_store,
    answer_question,
    inspect_index,
)

st.set_page_config(
    page_title="Data Indexing using RAG",
    page_icon="◈",
    layout="wide",
)

# ---------------- SESSION STATE ----------------
for key, default in {
    "pdf_index": None,
    "pdf_error": "",
    "chat_history": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------- THEME ----------------
st.markdown("""
<style>
.stApp {
    background: #110F14;
    color: #FFF8F0;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
}

[data-testid="stHeader"] {
    background: #110F14;
}

[data-testid="stSidebar"] {
    background: #211923;
    border-right: 1px solid #80566E;
}

[data-testid="stSidebar"] * {
    color: #FFF8F0;
}

h1, h2, h3, h4, p, label {
    color: #FFF8F0;
}

.hero {
    background: linear-gradient(125deg, #38243A, #512E46);
    border: 1px solid #B77D91;
    border-radius: 18px;
    padding: 30px;
    margin-bottom: 28px;
}

.eyebrow, .section-label {
    color: #F0C987;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
}

.hero h1 {
    color: #F0C987;
    font-family: Georgia, serif;
    font-size: 38px;
    line-height: 1.35;
}

.hero p {
    color: #FFF8F0;
    font-size: 16px;
}

/* UPLOADER: avoid styling its internal file row */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* The upload dropzone */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: #302337 !important;
    border: 1px dashed #B77D91 !important;
    border-radius: 10px !important;
}

/* Upload instructions */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] * {
    color: #FFF8F0 !important;
    -webkit-text-fill-color: #FFF8F0 !important;
}

/* Upload button */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
    background: #F0C987 !important;
    color: #211923 !important;
    border: 1px solid #F0C987 !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button * {
    color: #211923 !important;
    -webkit-text-fill-color: #211923 !important;
}

/* Custom filename card */
.pdf-card {
    background: #211923;
    border: 1px solid #B77D91;
    border-left: 5px solid #F0C987;
    border-radius: 10px;
    padding: 13px;
    margin: 12px 0;
    overflow-wrap: anywhere;
    word-break: break-word;
}

.pdf-card-label {
    color: #F0C987;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 7px;
}

.pdf-card-name {
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 700;
    overflow-wrap: anywhere;
    word-break: break-word;
}

.pdf-card-meta {
    color: #E5D4DF;
    font-size: 12px;
    margin-top: 5px;
}

/* Settings */
.setting-card {
    background: #342738;
    border: 1px solid #76556C;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 10px;
}

.setting-label {
    color: #F0C987;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}

.setting-value {
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 700;
    margin-top: 6px;
    overflow-wrap: anywhere;
}

/* Inputs */
.stTextInput input,
.stTextArea textarea {
    background: #251D29 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid #B77D91 !important;
    border-radius: 8px !important;
}

.stTextArea textarea {
    line-height: 1.7 !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    min-height: 44px;
    border-radius: 9px;
    font-weight: 800;
}

/* General button fallback */
.stButton > button {
    background: #F0C987 !important;
    color: #211923 !important;
    border: 1px solid #F0C987 !important;
}

/* Ask button */
.stFormSubmitButton > button {
    background: #9AD6B0 !important;
    color: #17251C !important;
    border: 1px solid #9AD6B0 !important;
}

/* Statistics */
.stat-card {
    background: #251D29;
    border: 1px solid #76556C;
    border-radius: 12px;
    padding: 15px;
    min-height: 90px;
    overflow-wrap: anywhere;
    word-break: break-word;
}

.stat-label {
    color: #E5D4DF;
    font-size: 12px;
}

.stat-value {
    color: #F0C987;
    font-size: 17px;
    font-weight: 800;
    margin-top: 8px;
    overflow-wrap: anywhere;
    word-break: break-word;
}

.answer-card {
    background: #29202D;
    border: 1px solid #B77D91;
    border-left: 5px solid #9AD6B0;
    border-radius: 10px;
    padding: 16px;
    color: #FFFFFF;
    line-height: 1.8;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

hr {
    border-color: #503B50;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ---------------- MAIN HEADING ----------------
st.markdown("""
<div class="hero">
    <div class="eyebrow">EXPERIMENT 12 / GENERATIVE AI LAB</div>
    <h1>Data Indexing using RAG</h1>
    <p>Upload a PDF, index its contents, and ask questions about your document.</p>
</div>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## ◈ Workspace")
    st.caption("DOCUMENT INTELLIGENCE")
    st.markdown("### Upload PDF")

    uploaded_pdf = st.file_uploader(
        "Choose a PDF from your computer",
        type=["pdf"],
        key="pdf_upload",
    )

    # Independently styled filename display
    if uploaded_pdf is not None:
        size_mb = uploaded_pdf.size / (1024 * 1024)

        st.markdown(
            f"""
            <div class="pdf-card">
                <div class="pdf-card-label">SELECTED PDF</div>
                <div class="pdf-card-name">
                    {html.escape(uploaded_pdf.name)}
                </div>
                <div class="pdf-card-meta">
                    {size_mb:.2f} MB · PDF document
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("""
        <div class="pdf-card">
            <div class="pdf-card-label">NO PDF SELECTED</div>
            <div class="pdf-card-name">
                Choose a PDF using the upload button above.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### Index settings")

    settings = [
        ("CHUNK SIZE", "1,000 characters"),
        ("OVERLAP", "150 characters"),]
    for label, value in settings:
        st.markdown(
            f"""
            <div class="setting-card">
                <div class="setting-label">{html.escape(label)}</div>
                <div class="setting-value">{html.escape(value)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    index_button = st.button(
        "◈ Index PDF",
        key="index_pdf_button",
        use_container_width=True,
    )

    clear_button = st.button(
        "Clear workspace",
        key="clear_pdf_button",
        use_container_width=True,
    )

    st.divider()
    st.caption("LOCAL PROCESSING · OLLAMA")


# ---------------- CLEAR ----------------
if clear_button:
    st.session_state.pdf_index = None
    st.session_state.pdf_error = ""
    st.session_state.chat_history = []
    st.rerun()


# ---------------- INDEX ----------------
if index_button:
    if uploaded_pdf is None:
        st.session_state.pdf_error = "Please upload a PDF first."
    else:
        st.session_state.pdf_error = ""
        st.session_state.pdf_index = None
        st.session_state.chat_history = []

        try:
            with st.spinner("Reading PDF and creating the index..."):
                documents = load_pdf(uploaded_pdf)
                chunks = split_documents(documents)
                vector_store = create_vector_store(chunks)
                checks = inspect_index(
                    documents,
                    chunks,
                    vector_store,
                )

                st.session_state.pdf_index = {
                    "name": uploaded_pdf.name,
                    "documents": documents,
                    "chunks": chunks,
                    "vector_store": vector_store,
                    "checks": checks,
                }

        except Exception as error:
            st.session_state.pdf_error = str(error)


if st.session_state.pdf_error:
    st.error(st.session_state.pdf_error)


# ---------------- WORKSPACE ----------------
data = st.session_state.pdf_index

if data:
    st.markdown(
        '<div class="section-label">01 / INDEX OVERVIEW</div>',
        unsafe_allow_html=True,
    )

    stats = [
        ("PDF FILE", data["name"]),
        ("TEXT PAGES", str(len(data["documents"]))),
        ("CHUNKS", str(len(data["chunks"]))),
        (
            "CHECKS PASSED",
            f'{sum(bool(v) for v in data["checks"].values())}'
            f'/{len(data["checks"])}',
        ),
    ]

    cols = st.columns(4)
    for col, (label, value) in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-label">{html.escape(label)}</div>
                    <div class="stat-value">{html.escape(value)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    ask_col, inspect_col = st.columns([1.7, 1])

    # ---------------- ASK QUESTIONS ----------------
    with ask_col:
        st.markdown(
            '<div class="section-label">02 / ASK YOUR DOCUMENT</div>',
            unsafe_allow_html=True,
        )
        st.markdown("### What would you like to know?")
        st.caption("Ask a question about the contents of your PDF.")

        with st.form("question_form", clear_on_submit=True):
            question = st.text_input(
                "Enter your question",
                placeholder="Ask something about your PDF...",
            )
            ask_button = st.form_submit_button(
                "✦ Ask PDF",
                use_container_width=True,
            )

        if ask_button:
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                try:
                    with st.spinner("Searching your PDF..."):
                        answer, retrieved = answer_question(
                            data["vector_store"],
                            question.strip(),
                        )

                    sources = []
                    for doc in retrieved:
                        sources.append({
                            "page": doc.metadata.get("page", "?"),
                            "text": doc.page_content,
                        })

                    st.session_state.chat_history.append({
                        "question": question.strip(),
                        "answer": answer,
                        "sources": sources,
                    })

                except Exception as error:
                    st.error(f"Could not answer the question: {error}")

        for i, item in enumerate(reversed(st.session_state.chat_history)):
            with st.container(border=True):
                st.markdown("**YOUR QUESTION**")
                st.write(item["question"])
                st.markdown("**ANSWER FROM YOUR PDF**")

                st.markdown(
                    f'<div class="answer-card">'
                    f'{html.escape(str(item["answer"]))}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                with st.expander("View retrieved source passages"):
                    for source in item["sources"]:
                        st.markdown(
                            f'**PDF page {html.escape(str(source["page"]))}**'
                        )
                        st.write(source["text"])

    # ---------------- INSPECTOR ----------------
    with inspect_col:
        st.markdown(
            '<div class="section-label">03 / INDEX INSPECTOR</div>',
            unsafe_allow_html=True,
        )
        st.markdown("### Consistency")

        for check_name, passed in data["checks"].items():
            if passed:
                st.success(f"✓ {check_name}")
            else:
                st.error(f"✗ {check_name}")

        st.divider()
        st.markdown("### Chunk browser")

        if data["chunks"]:
            selected_chunk = st.selectbox(
                "Choose a chunk",
                options=list(range(len(data["chunks"]))),
                format_func=lambda i: (
                    f'Chunk {i + 1} · Page '
                    f'{data["chunks"][i].metadata.get("page", "?")}'
                ),
            )

            chunk = data["chunks"][selected_chunk]
            page_number = chunk.metadata.get("page", "?")

            st.markdown(
                f"""
                <div class="setting-card">
                    <div class="setting-value">
                        Page {html.escape(str(page_number))}
                        · {len(chunk.page_content)} characters
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.text_area(
                "Chunk content",
                value=chunk.page_content,
                height=240,
                disabled=True,
                key=f"chunk_content_{selected_chunk}",
            )

        if all(data["checks"].values()):
            st.success("Index is ready for questions.")
        else:
            st.warning("Some consistency checks need attention.")

else:
    st.divider()
    st.markdown("### Your document workspace")
    st.write(
        "Upload a PDF from the sidebar and click **Index PDF**. "
        "After indexing, ask questions about the document."
    )
    st.info(
        "The vector index stays in memory during this app session. "
        "After restarting Streamlit, upload and index the PDF again."
    )


