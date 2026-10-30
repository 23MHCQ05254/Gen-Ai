
import io
import speech_recognition as sr
from google import genai
from gtts import gTTS


def transcribe_audio(audio_bytes):
    """Convert recorded audio into text."""
    if not audio_bytes:
        raise ValueError("Please record your voice first.")

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = recognizer.record(source)

        return recognizer.recognize_google(audio)

    except sr.UnknownValueError:
        raise ValueError("Speech not understood. Please speak clearly.")
    except sr.RequestError as exc:
        raise RuntimeError(f"Speech recognition error: {exc}")


def generate_response(user_text, api_key):
    """Generate an AI answer using Gemini."""
    if not user_text.strip():
        raise ValueError("Please enter or record a question.")

    if not api_key.strip():
        raise ValueError("Please enter your Gemini API key.")

    client = genai.Client(api_key=api_key.strip())

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            "You are a helpful voice assistant. Answer clearly and "
            "concisely, using language suitable for speech.\n\n"
            + user_text
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini did not return a response.")

    return response.text.strip()


def text_to_speech(text, language="en"):
    """Convert response text into MP3 audio."""
    if not text.strip():
        raise ValueError("There is no response to speak.")

    audio_buffer = io.BytesIO()
    tts = gTTS(text=text, lang=language)
    tts.write_to_fp(audio_buffer)

    return audio_buffer.getvalue()
