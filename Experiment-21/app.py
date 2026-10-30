
import io
import wave
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from main import generate_music


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MuseGAN Music Studio",
    page_icon="🎵",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff0f5, #f0eaff, #e5f7ff);
    color: #25223a;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

h1, h2, h3, p, label {
    color: #25223a !important;
}

.instrument-card {
    padding: 10px 6px;
    border-radius: 12px;
    text-align: center;
    min-height: 95px;
    margin-bottom: 12px;
    box-shadow: 0 3px 10px #00000010;
}

.instrument-card h4 {
    font-size: 17px;
    margin: 3px 0;
}

.instrument-card p {
    font-size: 12px;
    margin: 0;
}

.piano { background: #e8ddff; }
.bass { background: #d6f5fa; }
.melody { background: #ffe0ec; }
.drums { background: #ffe8cf; }

.stButton > button {
    border-radius: 10px;
    min-height: 43px;
    font-weight: 600;
    border: none;
}

div[data-testid="stAudio"] {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------
if "pattern" not in st.session_state:
    st.session_state.pattern = None

if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

if "music_generated" not in st.session_state:
    st.session_state.music_generated = False


# ---------------- AUDIO GENERATION ----------------
def make_wav(pattern, tempo=120, sample_rate=22050):
    """
    Convert the generated symbolic pattern into playable WAV audio.
    This lightweight synthesizer uses simple tones and drum sounds.
    """
    pattern = np.asarray(pattern)
    tracks, steps, pitches = pattern.shape

    step_duration = 60.0 / tempo / 4
    total_duration = steps * step_duration + 0.5
    audio = np.zeros(int(total_duration * sample_rate),
                     dtype=np.float32)

    track_ranges = [
        (48, 84),  # Piano
        (28, 52),  # Bass
        (60, 88),  # Melody
        (35, 50)   # Drums
    ]

    rng = np.random.default_rng(42)

    def add_tone(start_time, duration, frequency, amplitude,
                 waveform="sine"):
        start = int(start_time * sample_rate)
        length = min(
            int(duration * sample_rate),
            len(audio) - start
        )

        if length <= 0:
            return

        t = np.arange(length) / sample_rate
        envelope = np.exp(-4 * t / max(duration, 0.01))

        if waveform == "piano":
            sound = (
                np.sin(2 * np.pi * frequency * t)
                + 0.35 * np.sin(2 * np.pi * frequency * 2 * t)
                + 0.15 * np.sin(2 * np.pi * frequency * 3 * t)
            )
        elif waveform == "bass":
            sound = np.sin(2 * np.pi * frequency * t)
        elif waveform == "melody":
            sound = (
                np.sin(2 * np.pi * frequency * t)
                + 0.2 * np.sin(2 * np.pi * frequency * 2 * t)
            )
        else:
            sound = rng.normal(0, 1, length)

        audio[start:start + length] += (
            amplitude * sound * envelope
        ).astype(np.float32)

    for track in range(tracks):
        low, high = track_ranges[min(track, 3)]

        for step in range(steps):
            active = np.where(pattern[track, step] > 0.5)[0]

            for pitch_class in active:
                start_time = step * step_duration

                if track == 3:
                    # Simple kick, snare and hi-hat style sounds
                    if pitch_class % 3 == 0:
                        add_tone(start_time, 0.13, 65, 0.45)
                    elif pitch_class % 3 == 1:
                        add_tone(start_time, 0.09, 180, 0.22,
                                 waveform="noise")
                    else:
                        add_tone(start_time, 0.045, 7000, 0.10,
                                 waveform="noise")
                    continue

                # Choose a MIDI pitch in the instrument's range
                midi_pitch = low + (
                    (pitch_class - low % 12) % 12
                )

                while midi_pitch < low:
                    midi_pitch += 12

                while midi_pitch > high:
                    midi_pitch -= 12

                frequency = 440.0 * (2 ** ((midi_pitch - 69) / 12))

                if track == 0:
                    add_tone(start_time, step_duration * 0.9,
                             frequency, 0.12, "piano")
                elif track == 1:
                    add_tone(start_time, step_duration * 0.95,
                             frequency, 0.20, "bass")
                else:
                    add_tone(start_time, step_duration * 0.75,
                             frequency, 0.12, "melody")

    # Prevent clipping
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.85

    # WAV format: 16-bit mono PCM
    pcm = (audio * 32767).astype(np.int16)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())

    return buffer.getvalue()


# ---------------- HEADER ----------------



# ---------------- INSTRUMENT CARDS ----------------
st.markdown("### 🎼 Music Tracks")

c1, c2, c3, c4 = st.columns(4, gap="small")

with c1:
    st.markdown("""
    <div class="instrument-card piano">
        <h4>🎹 Piano</h4>
        <p>Chords and notes</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="instrument-card bass">
        <h4>🎸 Bass</h4>
        <p>Low-frequency notes</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="instrument-card melody">
        <h4>🎶 Melody</h4>
        <p>Main tune</p>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="instrument-card drums">
        <h4>🥁 Drums</h4>
        <p>Rhythm and beats</p>
    </div>
    """, unsafe_allow_html=True)


# ---------------- MUSIC SETTINGS ----------------
st.markdown("### ⚙️ Music Settings")

col1, col2, col3 = st.columns(3)

with col1:
    genre = st.selectbox(
        "Select Genre",
        ["Pop", "Classical", "Jazz", "Electronic"]
    )

with col2:
    tempo = st.slider("Tempo (BPM)", 60, 180, 120)

with col3:
    bars = st.selectbox("Number of Bars", [2, 4, 8], index=1)

epochs = st.slider("Training Epochs", 5, 30, 10)


# ---------------- ACTION BUTTONS ----------------
button1, button2 = st.columns(2, gap="small")

with button1:
    generate_clicked = st.button(
        "🎼 Generate Music",
        use_container_width=True,
        type="primary"
    )

with button2:
    play_clicked = st.button(
        "▶️ Play Music",
        use_container_width=True
    )


# ---------------- GENERATE MUSIC ----------------
if generate_clicked:
    with st.spinner("Generating music... Please wait."):
        try:
            midi, pattern = generate_music(
                genre=genre,
                tempo=tempo,
                bars=bars,
                epochs=epochs
            )

            st.session_state.pattern = np.asarray(pattern)
            st.session_state.audio_bytes = make_wav(
                st.session_state.pattern,
                tempo=tempo
            )
            st.session_state.music_generated = True

            st.success("Music generated successfully!")

        except Exception as error:
            st.session_state.pattern = None
            st.session_state.audio_bytes = None
            st.session_state.music_generated = False
            st.error(f"Music generation failed: {error}")


# ---------------- PLAY MUSIC ----------------
if play_clicked:
    if st.session_state.audio_bytes is None:
        st.warning("Please click Generate Music first.")
    else:
        st.markdown("### 🎧 Now Playing")
        st.audio(
            st.session_state.audio_bytes,
            format="audio/wav"
        )
        st.info(
            "Use the audio player's Play and Pause controls "
            "to listen to the generated music."
        )



# ---------------- VISUALIZATION ----------------
if st.session_state.pattern is not None:
    st.divider()
    st.markdown("### 📊 Generated Music Visualization")

    pattern = st.session_state.pattern
    names = ["Piano", "Bass", "Melody", "Drums"]

    left_col, right_col = st.columns(2, gap="medium")

    for index, name in enumerate(names):
        if index >= pattern.shape[0]:
            break

        # First and third graphs on the left;
        # second and fourth graphs on the right.
        target_col = left_col if index % 2 == 0 else right_col

        with target_col:
            fig, ax = plt.subplots(figsize=(5, 2.5))

            ax.imshow(
                pattern[index].T,
                aspect="auto",
                origin="lower",
                interpolation="nearest",
                cmap="magma"
            )

            ax.set_title(f"{name} Track")
            ax.set_xlabel("Time Steps")
            ax.set_ylabel("Pitch Class")
            fig.tight_layout()

            st.pyplot(fig)
            plt.close(fig)
