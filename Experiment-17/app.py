
import os
import streamlit as st
import pandas as pd
from PIL import Image

from main import (
    MODEL_PATH,
    train_model,
    load_trained_model,
    predict_image,
    load_saved_evaluation
)

st.set_page_config(
    page_title="Image Classification",
    layout="wide"
)

# ---------- CSS ----------
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

.upload-title {
    font-size: 20px;
    font-weight: bold;
    color: #17365D;
    margin-bottom: 10px;
}

.image-box {
    height: 360px;
    border: 2px solid #C9D5E5;
    border-radius: 12px;
    background: white;
    padding: 12px;
}

.prediction-box {
    height: 360px;
    border: 2px solid #C9D5E5;
    border-radius: 12px;
    background: white;
    padding: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.prediction-text {
    font-size: 25px;
    font-weight: bold;
    color: #17365D;
    overflow-wrap: anywhere;
    text-align: center;
}

.predicted-class {
    color: #16803C;
}

div.stButton > button {
    width: 100%;
    height: 45px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# ---------- TRAINING CONTROLS ----------
with st.sidebar:
    st.header("CNN Training")

    epochs = st.slider(
        "Maximum epochs", 1, 30, 10
    )

    batch_size = st.selectbox(
        "Batch size", [32, 64, 128], index=1
    )

    train_clicked = st.button(
        "Train CNN Model",
        type="primary",
        use_container_width=True
    )

    if os.path.exists(MODEL_PATH):
        st.success("Trained model available")
    else:
        st.warning("Train the model before predicting.")


if train_clicked:
    try:
        with st.spinner("Training CNN model..."):
            result = train_model(
                epochs=epochs,
                batch_size=batch_size
            )

        st.session_state["last_training"] = {
            "history": result["history"],
            "test_loss": result["test_loss"],
            "test_accuracy": result["test_accuracy"],
            "epochs_completed": result["epochs_completed"]
        }

        st.success("Training and evaluation completed.")

    except Exception as error:
        st.error(f"Training failed: {error}")


# ---------- IMAGE PREVIEW FUNCTION ----------
def fit_image_in_box(uploaded_file, box_size=(600, 320)):
    image = Image.open(uploaded_file).convert("RGB")

    # Resize while preserving the original aspect ratio
    image.thumbnail(box_size, Image.Resampling.LANCZOS)

    # Create a fixed-size background
    canvas = Image.new("RGB", box_size, "white")

    # Center the resized image inside the background
    x = (box_size[0] - image.width) // 2
    y = (box_size[1] - image.height) // 2

    canvas.paste(image, (x, y))

    return canvas


# ---------- IMAGE UPLOAD ----------
uploaded = st.file_uploader(
    "Choose an image",
    type=["png", "jpg", "jpeg", "bmp"],
    key="image_upload"
)


# ---------- TWO EQUAL-SIZE BOXES ----------
left, right = st.columns(2, gap="medium")

with left:
    st.markdown(
        '<div class="upload-title">UPLOAD IMAGE</div>',
        unsafe_allow_html=True
    )

    with st.container(height=390, border=True):
        if uploaded is not None:
            try:
                uploaded.seek(0)
                preview = fit_image_in_box(uploaded)
                st.image(
                    preview,
                    use_container_width=True
                )
            except Exception as error:
                st.error(f"Cannot display image: {error}")
        else:
            st.markdown(
                "<div style='height:320px;display:flex;"
                "align-items:center;justify-content:center;"
                "color:#777;'>Upload an image to preview</div>",
                unsafe_allow_html=True
            )


with right:
    st.markdown(
        '<div class="upload-title">PREDICTION</div>',
        unsafe_allow_html=True
    )

    with st.container(height=390, border=True):
        prediction = st.session_state.get("prediction_result")

        if prediction:
            st.markdown(
                f"""
                <div class="prediction-text">
                    PREDICTED:
                    <span class="predicted-class">
                        {prediction['class_name'].title()}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("")
            st.metric(
                "Confidence",
                f"{prediction['confidence']:.2f}%"
            )
        else:
            st.markdown(
                "<div style='height:320px;display:flex;"
                "align-items:center;justify-content:center;"
                "color:#777;'>Prediction will appear here</div>",
                unsafe_allow_html=True
            )


# ---------- BUTTONS ----------
col1, col2 = st.columns(2)

with col1:
    predict_clicked = st.button(
        "PREDICT",
        type="primary"
    )

with col2:
    reset_clicked = st.button("RESET")


if reset_clicked:
    st.session_state.pop("prediction_result", None)
    st.session_state.pop("image_upload", None)
    st.rerun()


if predict_clicked:
    if uploaded is None:
        st.warning("Please upload an image first.")
    else:
        try:
            uploaded.seek(0)

            with st.spinner("Predicting image..."):
                model = load_trained_model()

                class_name, confidence, probabilities = predict_image(
                    uploaded, model
                )

            st.session_state["prediction_result"] = {
                "class_name": class_name,
                "confidence": confidence,
                "probabilities": probabilities
            }

            st.rerun()

        except Exception as error:
            st.error(f"Prediction failed: {error}")


# ---------- CNN EVALUATION ----------
st.divider()
st.subheader("CNN Evaluation")

metrics = st.session_state.get("last_training")

if metrics is None:
    saved = load_saved_evaluation()

    if saved is not None:
        metrics = {
            "history": {
                "accuracy": saved["accuracy"],
                "val_accuracy": saved["val_accuracy"],
                "loss": saved["loss"],
                "val_loss": saved["val_loss"]
            },
            "test_loss": float(saved["test_loss"][0]),
            "test_accuracy": float(saved["test_accuracy"][0]),
            "epochs_completed": len(saved["loss"])
        }

if metrics:
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Test Accuracy",
        f"{metrics['test_accuracy'] * 100:.2f}%"
    )

    c2.metric(
        "Test Loss",
        f"{metrics['test_loss']:.4f}"
    )

    c3.metric(
        "Epochs Completed",
        metrics["epochs_completed"]
    )

    history = metrics["history"]

    st.write("Training and Validation Accuracy")
    st.line_chart(pd.DataFrame({
        "Training Accuracy": history["accuracy"],
        "Validation Accuracy": history["val_accuracy"]
    }))

    st.write("Training and Validation Loss")
    st.line_chart(pd.DataFrame({
        "Training Loss": history["loss"],
        "Validation Loss": history["val_loss"]
    }))
else:
    st.info("Train the CNN to display evaluation results.")
