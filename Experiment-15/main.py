
import re
import torch
import ollama
from diffusers import StableDiffusionPipeline


IMAGE_MODEL = "stable-diffusion-v1-5/stable-diffusion-v1-5"
VISION_MODEL = "llava:latest"

_pipeline = None


def load_image_model():
    global _pipeline

    if _pipeline is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        _pipeline = StableDiffusionPipeline.from_pretrained(
            IMAGE_MODEL,
            torch_dtype=dtype,
            safety_checker=None,
        )

        _pipeline = _pipeline.to(device)
        _pipeline.enable_attention_slicing()

    return _pipeline


def generate_image(prompt):
    if not prompt.strip():
        raise ValueError("Please enter an image prompt.")

    pipeline = load_image_model()

    result = pipeline(
        prompt=prompt.strip(),
        num_inference_steps=20,
        guidance_scale=7.0,
        height=512,
        width=512,
    )

    return result.images[0]


def understand_image(image, prompt):
    if image is None:
        raise ValueError("Generate an image first.")

    import io

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    response = ollama.chat(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    "Describe the image based on visible evidence. "
                    "Mention the objects, colors, background and "
                    "composition. Do not assume that every detail "
                    "in the original prompt is present. "
                    "Original prompt: " + prompt
                ),
                "images": [image_bytes],
            }
        ],
        options={"temperature": 0},
    )

    caption = response.message.content
    if not caption:
        raise RuntimeError("Ollama did not return a caption.")

    return caption.strip()


def calculate_alignment(prompt, caption):
    stop_words = {
        "the", "and", "for", "with", "from", "this", "that",
        "are", "was", "were", "into", "its", "image", "picture",
        "create", "generate", "show", "make", "a", "an", "in",
        "on", "of", "to", "is", "by", "it", "at"
    }

    def keywords(text):
        words = re.findall(r"[a-zA-Z0-9]+", text.lower())
        return {
            word for word in words
            if len(word) > 2 and word not in stop_words
        }

    prompt_words = keywords(prompt)
    caption_words = keywords(caption)

    matched = sorted(prompt_words & caption_words)
    missing = sorted(prompt_words - caption_words)

    score = (
        round(len(matched) / len(prompt_words) * 100)
        if prompt_words else 0
    )

    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "note": (
            "Keyword overlap is a simple estimate, not proof "
            "of visual similarity."
        ),
    }
