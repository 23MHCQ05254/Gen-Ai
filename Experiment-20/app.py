
import os
import tempfile
import streamlit as st
from html import escape

from main import summarize_video, answer_video_question

st.set_page_config(
    page_title="Video Intelligence AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg, #071323, #0b1930, #101c38
    );
    color: #FFFFFF;
}

header {
    background: transparent !important;
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero-title {
    color: #FFFFFF;
    font-size: 34px;
    font-weight: 800;
    text-align: center;
}

.hero-subtitle {
    color: #B9D4FF;
    text-align: center;
    margin-bottom: 30px;
}

.panel {
    background: #10213A;
    border: 1px solid #416797;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}

.panel-title {
    color: #70A7FF;
    font-size: 22px;
    font-weight: 750;
    margin-bottom: 8px;
}

.panel-description {
    color: #D2E2FA;
    font-size: 14px;
}

[data-testid="stFileUploader"],
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] section > div,
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
    background: #10213A !important;
    color: #FFFFFF !important;
    border-color: #416797 !important;
}

[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] label *,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span {
    color: #FFFFFF !important;
}

.stTextArea label,
.stTextArea label p {
    color: #FFFFFF !important;
}

.stTextArea textarea {
    background: #0B1B30 !important;
    color: #FFFFFF !important;
    border: 1px solid #416797 !important;
    border-radius: 10px !important;
}

.stButton button[kind="primary"] {
    background: linear-gradient(
        90deg, #2563EB, #6D5DFB
    ) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    min-height: 44px;
}

.response-box {
    background: #102B3A;
    color: #FFFFFF;
    border: 1px solid #35B8C9;
    border-radius: 14px;
    padding: 18px;
    margin-top: 14px;
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

.footer {
    text-align: center;
    color: #8FAFD9;
    margin-top: 30px;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-title">🎬 Video Intelligence AI</div>
<div class="hero-subtitle">
    Transformer-Based Video Analysis, Summarization
    and Video Question Answering
</div>
""", unsafe_allow_html=True)

# Initialize session state
defaults = {
    "video_path": None,
    "video_signature": None,
    "video_summary": "",
    "video_answer": "",
    "video_question": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


left, right = st.columns(2, gap="large")

# LEFT COLUMN: Upload and preview
with left:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">📹 Upload Video</div>
        <div class="panel-description">
            Upload a video to analyze its scenes and events.
            Supported formats: MP4, MOV, AVI, MKV.
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Browse Video",
        type=["mp4", "mov", "avi", "mkv"],
        key="video_uploader"
    )

    if uploaded_file is not None:
        signature = (
            uploaded_file.name,
            uploaded_file.size
        )

        if signature != st.session_state.video_signature:
            # Remove the previous temporary video
            old_path = st.session_state.video_path

            if old_path and os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    pass

            suffix = os.path.splitext(
                uploaded_file.name
            )[1].lower()

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                st.session_state.video_path = temp_file.name

            st.session_state.video_signature = signature
            st.session_state.video_summary = ""
            st.session_state.video_answer = ""

        st.video(uploaded_file)

        st.caption(
            f"File: {uploaded_file.name} | "
            f"{uploaded_file.size / (1024 * 1024):.2f} MB"
        )


# RIGHT COLUMN: Analyze and ask questions
with right:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">🔍 Video Analysis</div>
        <div class="panel-description">
            Analyze scenes, identify events, and summarize
            the video chronologically using a video Transformer.
        </div>
    </div>
    """, unsafe_allow_html=True)

    analyze_clicked = st.button(
        "✨ Analyze & Summarize Video",
        type="primary",
        use_container_width=True
    )

    if analyze_clicked:
        video_path = st.session_state.video_path

        if not video_path or not os.path.exists(video_path):
            st.warning("Please upload a video first.")
        else:
            try:
                with st.spinner(
                    "Transformer is analyzing the video. "
                    "The first run may take several minutes..."
                ):
                    st.session_state.video_summary = summarize_video(
                        video_path
                    )

                st.session_state.video_answer = ""
                st.success("Video analysis completed!")

            except Exception as error:
                st.error(
                    f"Video analysis failed: {error}"
                )

    # Summary directly below analysis button
    if st.session_state.video_summary:
        st.markdown(
            '<div class="response-box">'
            '<div class="response-title">📝 Video Summary</div>'
            + escape(st.session_state.video_summary)
            + '</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="panel">
            <div class="panel-title">💬 Video Question Answering</div>
            <div class="panel-description">
                Ask a question about the uploaded video.
            </div>
        </div>
        """, unsafe_allow_html=True)

        question = st.text_area(
            "Your question",
            placeholder=(
                "Example: What happens at the beginning "
                "of the video?"
            ),
            height=100,
            key="video_question_input"
        )

        ask_clicked = st.button(
            "💡 Get Answer",
            type="primary",
            use_container_width=True
        )

        if ask_clicked:
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                try:
                    with st.spinner(
                        "Finding the answer from the video..."
                    ):
                        st.session_state.video_answer = (
                            answer_video_question(
                                st.session_state.video_path,
                                question.strip()
                            )
                        )

                except Exception as error:
                    st.error(
                        f"Could not answer the question: {error}"
                    )

        # Answer directly below Get Answer button
        if st.session_state.video_answer:
            st.markdown(
                '<div class="response-box">'
                '<div class="response-title">💡 Answer</div>'
                + escape(st.session_state.video_answer)
                + '</div>',
                unsafe_allow_html=True
            )

    if st.button(
        "🗑️ Clear Results",
        use_container_width=True
    ):
        st.session_state.video_summary = ""
        st.session_state.video_answer = ""
        st.rerun()



