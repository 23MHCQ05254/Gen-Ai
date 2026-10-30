
import torch
import av
from PIL import Image
from transformers import (
    Qwen2_5_VLForConditionalGeneration,
    AutoProcessor,
)
from qwen_vl_utils import process_vision_info

MODEL_NAME = "Qwen/Qwen2.5-VL-3B-Instruct"

# Memory and speed settings
SAMPLE_FPS = 0.2          # Approximately one frame every 5 seconds
MAX_FRAMES = 12           # Limit frames sent to the model
MAX_IMAGE_SIZE = 448      # Resize images to reduce memory use
MAX_NEW_TOKENS = 300

_model = None
_processor = None


def load_model():
    """Load the model once and reuse it."""
    global _model, _processor

    if _model is None:
        _processor = AutoProcessor.from_pretrained(MODEL_NAME)

        _model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            MODEL_NAME,
            torch_dtype="auto",
            device_map="auto",
            low_cpu_mem_usage=True,
        )

        _model.eval()

    return _model, _processor


def extract_video_frames(video_path, fps=SAMPLE_FPS):
    """Extract ordered video frames using PyAV."""
    frames = []

    with av.open(video_path) as container:
        if not container.streams.video:
            raise ValueError("The uploaded file has no video stream.")

        video_stream = container.streams.video[0]
        source_fps = float(video_stream.average_rate or 24.0)
        frame_interval = max(1, round(source_fps / fps))

        for index, frame in enumerate(container.decode(video_stream)):
            if index % frame_interval != 0:
                continue

            image = frame.to_image().convert("RGB")
            image.thumbnail(
                (MAX_IMAGE_SIZE, MAX_IMAGE_SIZE),
                Image.Resampling.LANCZOS,
            )
            frames.append(image)

            if len(frames) >= MAX_FRAMES:
                break

    if not frames:
        raise ValueError("No frames could be extracted from the video.")

    return frames


def analyze_video(video_path, task_prompt):
    """Analyze sampled video frames in chronological order."""
    model, processor = load_model()

    frames = extract_video_frames(video_path)

    # Use ordered images instead of the video decoder.
    content = [
        {"type": "image", "image": frame}
        for frame in frames
    ]

    content.append({
        "type": "text",
        "text": task_prompt,
    })

    messages = [{
        "role": "user",
        "content": content,
    }]

    prompt = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    image_inputs, video_inputs = process_vision_info(messages)

    inputs = processor(
        text=[prompt],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )

    # Supports models whose parameters are offloaded across devices.
    inputs = inputs.to(_model_input_device(model))

    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
        )

    # Remove the input tokens from the generated output.
    generated_ids = [
        output[len(input_ids):]
        for input_ids, output in zip(inputs.input_ids, output_ids)
    ]

    answer = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True,
    )[0].strip()

    return answer


def _model_input_device(model):
    """Find a suitable device for model inputs."""
    try:
        return model.get_input_embeddings().weight.device
    except (AttributeError, RuntimeError):
        return next(model.parameters()).device


def summarize_video(video_path):
    """Create a chronological video summary."""
    prompt = """
Analyze the supplied video frames in their original order.

Write your answer using these sections:

1. OVERVIEW
Explain the main activity or purpose of the video.

2. CHRONOLOGICAL EVENTS
Describe the visible events from beginning to end in time order.
Mention scene changes and actions when visible.

3. IMPORTANT DETAILS
Mention important people, objects, actions, and surroundings.

4. CONCLUSION
Give a short overall summary.

Rules:
- Use only information supported by the frames.
- Do not invent events, identities, dialogue, or timestamps.
- The video is sampled sparsely, so some actions may be missed.
- Keep events in chronological order.
"""
    return analyze_video(video_path, prompt)


def answer_video_question(video_path, question):
    """Answer a question using the sampled video frames."""
    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    prompt = f"""
Answer the following question using the supplied video frames.

Question: {question.strip()}

Instructions:
- Consider the visual content and order of the frames.
- Give a clear, direct answer.
- Do not invent details.
- Audio is not analyzed, so do not claim to hear speech.
- If the frames do not provide enough evidence, say so.
"""
    return analyze_video(video_path, prompt)
