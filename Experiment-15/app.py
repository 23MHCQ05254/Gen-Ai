
import io
import streamlit as st

from main import (
    generate_image,
    understand_image,
    calculate_alignment,
)

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Multimodal Prompt Lab",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- CUSTOM CSS ----------------

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #111827, #241442, #111827);
        color: white;
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    .hero {
        background: linear-gradient(100deg, #7c3aed, #db2777);
        padding: 28px;
        border-radius: 18px;
        text-align: center;
        margin-bottom: 24px;
    }

    .hero h1 {
        color: white;
        margin: 0;
        font-size: 34px;
    }

    .hero p {
        color: white;
        margin-top: 10px;
        font-size: 16px;
    }

    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 10px !important;
    }

    div[data-testid="stTextArea"] textarea::placeholder {
        color: #555555 !important;
        opacity: 1 !important;
    }

    div.stButton > button {
        width: 100%;
        min-height: 44px;
        border-radius: 10px;
        background: linear-gradient(90deg, #7c3aed, #c026d3);
        color: white;
        border: none;
        font-weight: 600;
    }

    div.stButton > button:hover {
        border: 1px solid white;
        color: white;
    }

    div[data-testid="stDownloadButton"] button {
        width: 100%;
        border-radius: 10px;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- DEFAULT PROMPT ----------------

DEFAULT_PROMPT = (
    "A beautiful golden retriever sitting on green grass "
    "in a sunny garden, colorful flowers surrounding it, "
    "soft natural sunlight, realistic photography, "
    "detailed background, balanced composition."
)

# ---------------- SESSION STATE ----------------

if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

if "original_prompt" not in st.session_state:
    st.session_state.original_prompt = DEFAULT_PROMPT

if "caption" not in st.session_state:
    st.session_state.caption = ""

if "comparison" not in st.session_state:
    st.session_state.comparison = None


def image_to_png_bytes(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


# ---------------- HEADER ----------------

st.markdown(
    """
    <div class="hero">
        <h1>🎨 Multimodal Prompt Lab</h1>
        <p>
            Generate images locally, understand visual content,
            and evaluate prompt alignment.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- PROMPT INPUT ----------------

st.markdown("### ✍️ Step 1: Enter Your Image Prompt")

st.write(
    "The default prompt is provided below. You can edit it "
    "or enter your own detailed description."
)

prompt = st.text_area(
    "Image prompt",
    value=st.session_state.original_prompt,
    height=140,
    key="prompt_input",
)

# ---------------- BUTTONS ----------------

col1, col2 = st.columns(2)

with col1:
    generate_clicked = st.button(
        "🎨 Generate Image",
        use_container_width=True,
    )

with col2:
    reset_clicked = st.button(
        "🔄 Start Again",
        use_container_width=True,
    )

# ---------------- RESET ----------------

if reset_clicked:
    st.session_state.generated_image = None
    st.session_state.original_prompt = DEFAULT_PROMPT
    st.session_state.caption = ""
    st.session_state.comparison = None

    st.rerun()

# ---------------- GENERATE IMAGE ----------------

if generate_clicked:
    if not prompt.strip():
        st.warning("Please enter an image prompt.")
    else:
        try:
            with st.spinner(
                "Loading the local model and generating your image..."
            ):
                image = generate_image(prompt.strip())

            st.session_state.generated_image = image
            st.session_state.original_prompt = prompt.strip()
            st.session_state.caption = ""
            st.session_state.comparison = None

            st.success("Image generated successfully!")

        except Exception as error:
            st.error("Image generation failed.")
            st.code(str(error))
            st.info(
                "The first run downloads the Stable Diffusion model. "
                "Check your internet connection, RAM, disk space, "
                "and PyTorch installation."
            )

# ---------------- DISPLAY GENERATED IMAGE ----------------

if st.session_state.generated_image is not None:
    st.divider()

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("### 🖼️ Step 2: Generated Image")

        st.image(
            st.session_state.generated_image,
            use_container_width=True,
        )

        st.download_button(
            label="⬇️ Download Generated Image",
            data=image_to_png_bytes(
                st.session_state.generated_image
            ),
            file_name="generated_image.png",
            mime="image/png",
            use_container_width=True,
        )

    with right:
        st.markdown("### 📝 Original Prompt")
        st.write(st.session_state.original_prompt)

        st.markdown("### 🔍 Step 3: Image Understanding")

        if st.button(
            "Analyze Image with Ollama",
            use_container_width=True,
        ):
            try:
                with st.spinner(
                    "LLaVA is analyzing the generated image..."
                ):
                    caption = understand_image(
                        st.session_state.generated_image,
                        st.session_state.original_prompt,
                    )

                st.session_state.caption = caption

                st.session_state.comparison = calculate_alignment(
                    st.session_state.original_prompt,
                    caption,
                )

            except Exception as error:
                st.error("Image analysis failed.")
                st.code(str(error))
                st.info(
                    "Make sure Ollama is running and llava:latest "
                    "is installed."
                )

        if st.session_state.caption:
            st.markdown("### 🤖 Image Understanding Output")
            st.write(st.session_state.caption)

    # ---------------- COMPARISON ----------------

    if st.session_state.comparison:
        st.divider()
        st.markdown("### 📊 Step 4: Prompt Alignment Comparison")

        result = st.session_state.comparison

        metric_col, matched_col, missing_col = st.columns(3)

        with metric_col:
            st.metric(
                "Keyword Overlap",
                f"{result['score']}%",
            )

        with matched_col:
            st.markdown("**✅ Matched Keywords**")
            st.write(
                ", ".join(result["matched"])
                if result["matched"]
                else "None"
            )

        with missing_col:
            st.markdown("**⚠️ Missing Keywords**")
            st.write(
                ", ".join(result["missing"])
                if result["missing"]
                else "None"
            )

        st.info(result["note"])

        with st.expander("View Full Comparison"):
            st.markdown("**Original Prompt**")
            st.write(st.session_state.original_prompt)

            st.markdown("**Image Caption**")
            st.write(st.session_state.caption)

            st.markdown("**Evaluation Result**")
            st.write(
                f"Keyword overlap: {result['score']}%"
            )


