import streamlit as st
from main import generate_stylized_image
from PIL import Image
import io

st.set_page_config(
    page_title="Neural Style Transfer",
    page_icon="🎨",
    layout="wide"
)

# -------------------- CSS DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #101827, #202b45);
    color: white;
}

h1, h2, h3, p, label {
    color: white !important;
}

/* Buttons */
div.stButton > button,
div.stDownloadButton > button {
    background: linear-gradient(90deg, #7c3aed, #ec4899) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px !important;
    font-weight: bold !important;
}

/* Purple and pink upload area */
[data-testid="stFileUploader"] section {
    background: linear-gradient(90deg, #7c3aed, #ec4899) !important;
    border: 2px solid #c084fc !important;
    border-radius: 12px !important;
}

/* Upload button */
[data-testid="stFileUploader"] button {
    background: #6d28d9 !important;
    color: white !important;
    border: 1px solid #e9d5ff !important;
    border-radius: 8px !important;
}

/* Text inside the coloured upload area */
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] section span,
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section button {
    color: white !important;
}

/* Uploaded filename and file information */
[data-testid="stFileUploaderFileName"],
[data-testid="stFileUploaderFile"] small {
    color: #ffffff !important;
}

/* Slider */
div[data-testid="stSlider"] [role="slider"] {
    background-color: #ec4899 !important;
}

/* Consistent spacing */
div[data-testid="stVerticalBlock"] {
    gap: 1rem;
}
</style>
""", unsafe_allow_html=True)


# -------------------- IMAGE PREVIEW --------------------

def make_preview(image, width=500, height=500):
    """Display every image inside an equal-sized box."""
    image = image.copy().convert("RGB")

    image.thumbnail(
        (width, height),
        Image.Resampling.LANCZOS
    )

    # Dark canvas keeps the image box consistent
    canvas = Image.new(
        "RGB",
        (width, height),
        (25, 35, 55)
    )

    x = (width - image.width) // 2
    y = (height - image.height) // 2

    canvas.paste(image, (x, y))
    return canvas


# -------------------- APPLICATION TITLE --------------------

st.title("🎨 Neural Style Transfer")

st.caption(
    "Combine a photograph with the artistic style of a painting "
    "using a pretrained VGG19 CNN."
)

st.divider()


# -------------------- IMAGE UPLOADS --------------------

left, right = st.columns(2, gap="large")

content_image = None
style_image = None

with left:
    st.subheader("📷 Content Image")
    st.write("Upload the photograph you want to transform.")

    content_file = st.file_uploader(
        "Choose content image",
        type=["jpg", "jpeg", "png"],
        key="content"
    )

    if content_file is not None:
        content_image = Image.open(
            io.BytesIO(content_file.getvalue())
        ).convert("RGB")

        st.image(
            make_preview(content_image),
            caption="Content Image",
            width=500
        )

with right:
    st.subheader("🖼️ Style Image")
    st.write("Upload the painting whose style you want to apply.")

    style_file = st.file_uploader(
        "Choose style image",
        type=["jpg", "jpeg", "png"],
        key="style"
    )

    if style_file is not None:
        style_image = Image.open(
            io.BytesIO(style_file.getvalue())
        ).convert("RGB")

        st.image(
            make_preview(style_image),
            caption="Style Image",
            width=500
        )


# -------------------- GENERATION SETTINGS --------------------

st.divider()
st.subheader("⚙️ Generation Settings")

steps = st.slider(
    "Optimization steps",
    min_value=10,
    max_value=100,
    value=30,
    step=10,
    help="More steps may improve the result but take longer."
)


# -------------------- GENERATE IMAGE --------------------

if st.button(
    "✨ Generate Stylized Image",
    use_container_width=True
):
    if content_file is None or style_file is None:
        st.warning(
            "Please upload both a content image and a style image."
        )
    else:
        try:
            with st.spinner(
                "Generating artwork. This may take several minutes..."
            ):
                result = generate_stylized_image(
                    content_file.getvalue(),
                    style_file.getvalue(),
                    steps=steps
                )

            st.session_state["nst_result"] = result
            st.success("Neural Style Transfer completed!")

        except Exception as error:
            st.error(f"Generation failed: {error}")
            st.info(
                "Check the VS Code terminal for the complete error."
            )


# -------------------- GENERATED IMAGE --------------------

if "nst_result" in st.session_state:
    st.divider()
    st.subheader("🌟 Generated Artwork")

    result = st.session_state["nst_result"]

    # Same 500 x 500 preview size as both input images
    st.image(
        make_preview(result, width=500, height=500),
        caption="Generated Stylized Image",
        width=500
    )

    buffer = io.BytesIO()
    result.save(buffer, format="PNG")

    st.download_button(
        "⬇️ Download Generated Image",
        data=buffer.getvalue(),
        file_name="neural_style_transfer.png",
        mime="image/png",
        use_container_width=True
    )


# -------------------- CLEAR RESULTS --------------------

if st.button("🗑️ Clear Results"):
    st.session_state.pop("nst_result", None)
    st.rerun()

