
import os
import html
import streamlit as st
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder

from main import transcribe_audio, generate_response, text_to_speech

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

st.set_page_config(
    page_title="Bidirectional Speech AI",
    page_icon="🎙️",
    layout="wide"
)

# ---------------- GUI DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f1f0ff, #e9faff, #fff0f6);
}
.block-container {
    max-width: 1100px;
    padding-top: 1.5rem;
}
.hero {
    background: linear-gradient(110deg, #5146e5, #8b5cf6, #ec4899);
    padding: 25px;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(79, 70, 229, .18);
}
.hero h1 {
    color: white;
    margin: 0;
}
.hero p {
    color: white;
    margin-bottom: 0;
}
div.stButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
}

/* Recognized Text input box */
div[data-testid="stTextArea"] textarea {
    background-color: #F0E7FF !important;
    color: #54258A !important;
    border: 1px solid #B794F4 !important;
    border-radius: 12px !important;
    font-size: 17px !important;
    line-height: 1.6 !important;
    caret-color: #7C3AED !important;
}

/* Input placeholder */
div[data-testid="stTextArea"] textarea::placeholder {
    color: #9575CD !important;
    opacity: 1 !important;
}

/* Matching response box */
.ai-response-box {
    background-color: #F0E7FF;
    color: #54258A;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #B794F4;
    height: 190px;
    overflow-y: auto;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
    font-size: 17px;
    line-height: 1.6;
}
.ai-response-placeholder {
    background-color: #F0E7FF;
    color: #9575CD;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #B794F4;
    height: 190px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-size: 16px;
}
</style>

<div class="hero">
    <h1>🎙️ Bidirectional Speech AI</h1>
    <p>Speak naturally • Ask Gemini • Listen to the answer</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
defaults = {
    "recognized_text": "",
    "ai_response": "",
    "spoken_audio": None,
    "last_audio_id": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------- SETTINGS ----------------
with st.sidebar:
    st.header("⚙️ Settings")

    if API_KEY:
        st.success("Gemini API key is configured.")
    else:
        st.error("Gemini API key not found in .env")

    st.caption("Your API key is loaded from the .env file.")

# ---------------- VOICE INPUT ----------------
st.markdown("### 🎧 Step 1: Record Your Voice")
st.write(
    "Click Start Recording, allow microphone access, speak your question, "
    "and click Stop Recording."
)

recording = mic_recorder(
    start_prompt="🎙️ Start Recording",
    stop_prompt="⏹️ Stop Recording",
    key="voice_recorder",
    use_container_width=True,
    format="wav",
)

if recording and recording.get("bytes"):
    audio_bytes = recording["bytes"]
    audio_id = str(hash(audio_bytes))

    if st.session_state.last_audio_id != audio_id:
        st.session_state.last_audio_id = audio_id

        try:
            with st.spinner("Converting speech to text..."):
                recognized = transcribe_audio(audio_bytes)

            st.session_state.recognized_text = recognized
            st.session_state.ai_response = ""
            st.session_state.spoken_audio = None
            st.success("Speech recognized successfully!")

        except Exception as e:
            st.error(f"Speech recognition error: {e}")

# ---------------- TEXT AND RESPONSE ----------------
left, right = st.columns(2, gap="large")

with left:
    st.markdown("### 📝 Recognized Text")

    st.text_area(
        "Your question",
        key="recognized_text",
        height=190,
        placeholder="Record your voice or type a question here..."
    )

    if st.button("🧹 Clear Input", use_container_width=True):
        st.session_state.recognized_text = ""
        st.session_state.last_audio_id = None
        st.session_state.ai_response = ""
        st.session_state.spoken_audio = None
        st.rerun()

with right:
    st.markdown("### 🤖 Gemini AI Response")

    if st.session_state.ai_response:
        safe_response = html.escape(st.session_state.ai_response)

        st.markdown(
            f'<div class="ai-response-box">{safe_response}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="ai-response-placeholder">'
            'Your generated answer will appear here.'
            '</div>',
            unsafe_allow_html=True
        )

    if st.button("🧹 Clear Output", use_container_width=True):
        st.session_state.ai_response = ""
        st.session_state.spoken_audio = None
        st.rerun()


# ---------------- ACTION BUTTONS ----------------


generate_col, speak_col = st.columns(2, gap="medium")

with generate_col:
    if st.button(
        "🤖 Generate Gemini Response",
        type="primary",
        use_container_width=True
    ):
        if not API_KEY:
            st.error(
                "Gemini API key is missing. Check the .env file "
                "and restart the application."
            )

        elif not st.session_state.recognized_text.strip():
            st.warning("Record your voice or type a question first.")

        else:
            try:
                with st.spinner("Gemini is generating your answer..."):
                    answer = generate_response(
                        st.session_state.recognized_text,
                        API_KEY
                    )

                st.session_state.ai_response = answer
                st.session_state.spoken_audio = None
                st.rerun()

            except Exception as e:
                st.error(f"Gemini error: {e}")

with speak_col:
    if st.button(
        "🔊 Speak Response",
        use_container_width=True
    ):
        if not st.session_state.ai_response.strip():
            st.warning("Generate a Gemini response first.")

        else:
            try:
                with st.spinner("Creating speech audio..."):
                    audio = text_to_speech(
                        st.session_state.ai_response
                    )

                st.session_state.spoken_audio = audio

            except Exception as e:
                st.error(f"Text-to-Speech error: {e}")

# ---------------- AUDIO PLAYER ----------------
if st.session_state.spoken_audio:
    st.markdown("### 🔈 Listen to the Response")
    st.audio(
        st.session_state.spoken_audio,
        format="audio/mp3"
    )
