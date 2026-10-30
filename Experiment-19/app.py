
import streamlit as st
from PIL import Image
from html import escape
from main import answer_question

st.set_page_config(
    page_title="Vision AI - VQA",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #071323, #0b1930, #101c38);
    color: #FFFFFF;
}

header { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero-title {
    color: #FFFFFF;
    font-size: 36px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 8px;
}

.hero-subtitle {
    color: #B9D4FF;
    text-align: center;
    font-size: 16px;
    margin-bottom: 30px;
}

.panel {
    background: #10213A;
    border: 1px solid #416797;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 15px;
}

.panel-title {
    color: #70A7FF;
    font-size: 23px;
    font-weight: 750;
    margin-bottom: 8px;
}

.panel-description {
    color: #D2E2FA;
    font-size: 14px;
}

/* Keep uploader dark before and after selecting a file */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] section > div,
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] > div,
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] > div > div,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] > div,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] > div > div {
    background-color: #10213A !important;
    color: #FFFFFF !important;
    border-color: #416797 !important;
    box-shadow: none !important;
}

/* Upload area border */
[data-testid="stFileUploader"] section {
    border: 1px dashed #70A7FF !important;
    border-radius: 14px !important;
    padding: 12px !important;
}

/* Uploaded filename, icon and instructions */
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] label *,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] svg {
    color: #FFFFFF !important;
    fill: currentColor;
}

/* Browse button */
[data-testid="stFileUploader"] button {
    background: #2563EB !important;
    color: #FFFFFF !important;
    border: 1px solid #60A5FA !important;
    border-radius: 8px !important;
}

/* Question box */
.stTextArea label,
.stTextArea label p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

.stTextArea textarea {
    background: #0B1B30 !important;
    color: #FFFFFF !important;
    border: 1px solid #416797 !important;
    border-radius: 10px !important;
    caret-color: #70A7FF !important;
}

.stTextArea textarea::placeholder {
    color: #C4D7F5 !important;
    opacity: 1 !important;
}

/* Generate button */
.stButton button[kind="primary"] {
    background: linear-gradient(90deg, #2563EB, #6D5DFB) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 12px !important;
}

/* Response directly below Generate Answer */
.response-box {
    background: #102B3A;
    color: #FFFFFF;
    border: 1px solid #35B8C9;
    border-radius: 14px;
    padding: 18px;
    margin-top: 16px;
    line-height: 1.7;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.response-title {
    color: #70A7FF;
    font-size: 21px;
    font-weight: 750;
    margin-bottom: 10px;
}

[data-testid="stImage"] img {
    border-radius: 12px;
    border: 1px solid #416797;
}

.footer {
    color: #8FAFD9;
    text-align: center;
    font-size: 13px;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-title">👁️ Vision AI</div>
<div class="hero-subtitle">
    Visual Question Answering using Ollama + LLaVA
</div>
""", unsafe_allow_html=True)

if "vqa_answer" not in st.session_state:
    st.session_state.vqa_answer = ""

left_col, right_col = st.columns(2, gap="large")

# LEFT SIDE: IMAGE UPLOAD
with left_col:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">🖼️ Upload Image</div>
        <div class="panel-description">
            Choose an image file (JPG, PNG, or WEBP).
            Your image will appear below.
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Browse Image",
        type=["jpg", "jpeg", "png", "webp"],
        key="vqa_uploader"
    )

    current_image = None

    if uploaded_file is not None:
        try:
            current_image = Image.open(uploaded_file).convert("RGB")
            st.image(
                current_image,
                caption="Uploaded Image",
                use_container_width=True
            )
        except Exception:
            st.error("Unable to open the image. Please try another.")

# RIGHT SIDE: QUESTION + RESPONSE
with right_col:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">💬 Ask a Question</div>
        <div class="panel-description">
            Enter a question about the uploaded image.
        </div>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_area(
        "Your question",
        placeholder="Example: What is the dog doing?",
        height=130,
        key="vqa_question"
    )

    generate = st.button(
        "✦ Generate Answer",
        type="primary",
        use_container_width=True
    )

    if generate:
        if current_image is None:
            st.warning("Please upload an image first.")
        elif not question.strip():
            st.warning("Please enter your question.")
        else:
            try:
                with st.spinner("LLaVA is analyzing your image..."):
                    st.session_state.vqa_answer = answer_question(
                        current_image,
                        question.strip()
                    )
            except Exception as error:
                st.session_state.vqa_answer = ""
                st.error(f"Unable to generate answer: {error}")

    # RESPONSE APPEARS DIRECTLY BELOW THE BUTTON
    if st.session_state.vqa_answer:
        st.markdown(
            '<div class="response-box">'
            '<div class="response-title">✨ AI Response</div>'
            + escape(st.session_state.vqa_answer)
            + '</div>',
            unsafe_allow_html=True
        )

        if st.button("🗑️ Clear Result", use_container_width=True):
            st.session_state.vqa_answer = ""
            st.rerun()


