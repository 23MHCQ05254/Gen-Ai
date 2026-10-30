
import random

import numpy as np
import pretty_midi
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# ==========================================================
# CONFIGURATION
# ==========================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

TRACK_NAMES = ["Piano", "Bass", "Melody", "Drums"]

LATENT_SIZE = 64
STEPS_PER_BAR = 16
PITCH_CLASSES = 12

TRACK_RANGES = {
    "Piano": (48, 84),
    "Bass": (32, 55),
    "Melody": (60, 88),
    "Drums": (35, 51),
}


# ==========================================================
# GENERATOR
# ==========================================================

class MusicGenerator(nn.Module):
    def __init__(self, output_size):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(LATENT_SIZE, 256),
            nn.LeakyReLU(0.2),

            nn.Linear(256, 512),
            nn.LeakyReLU(0.2),

            nn.Linear(512, output_size),
            nn.Sigmoid()
        )

    def forward(self, noise):
        return self.network(noise)


# ==========================================================
# DISCRIMINATOR
# ==========================================================

class MusicDiscriminator(nn.Module):
    def __init__(self, input_size):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.2),

            nn.Linear(512, 128),
            nn.LeakyReLU(0.2),

            nn.Linear(128, 1)
        )

    def forward(self, music):
        return self.network(music)


# ==========================================================
# CREATE SYMBOLIC TRAINING PATTERNS
# ==========================================================

def create_training_data(bars, genre, samples=160):
    """
    Creates simple rule-based symbolic patterns for training
    an educational GAN demonstration.

    Shape:
        (4 tracks, time steps, 12 pitch classes)
    """

    total_steps = bars * STEPS_PER_BAR
    data = []

    scales = {
        "Pop": [0, 2, 4, 5, 7, 9, 11],
        "Classical": [0, 2, 4, 5, 7, 9, 11],
        "Jazz": [0, 2, 3, 4, 7, 9, 10],
        "Electronic": [0, 2, 4, 5, 7, 9, 11],
    }

    scale = scales.get(genre, scales["Pop"])
    chord_progression = [0, 5, 7, 0]

    for _ in range(samples):
        pattern = np.zeros(
            (4, total_steps, PITCH_CLASSES),
            dtype=np.float32
        )

        root = random.choice([0, 2, 4, 5, 7, 9])

        for step in range(total_steps):
            bar_index = step // STEPS_PER_BAR
            position = step % STEPS_PER_BAR

            chord_root = (
                root + chord_progression[bar_index % 4]
            ) % 12

            # PIANO: chord notes on beats
            if position in [0, 4, 8, 12]:
                for interval in [0, 4, 7]:
                    pitch_class = (
                        chord_root + interval
                    ) % 12

                    pattern[0, step, pitch_class] = 1.0

            # BASS: root notes
            if position in [0, 8]:
                pattern[1, step, chord_root] = 1.0

            # MELODY: notes from the selected scale
            melody_probability = (
                0.35 if genre == "Electronic" else 0.22
            )

            if random.random() < melody_probability:
                interval = random.choice(scale)

                pitch_class = (root + interval) % 12

                pattern[2, step, pitch_class] = 1.0

            # DRUMS: kick and snare-like events
            if position in [0, 8]:
                pattern[3, step, 0] = 1.0

            if position in [4, 12]:
                pattern[3, step, 2] = 1.0

            # Small random variation
            if random.random() < 0.03:
                track_index = random.randrange(3)
                pitch_class = random.randrange(12)

                pattern[
                    track_index, step, pitch_class
                ] = 1.0

        data.append(pattern.reshape(-1))

    return torch.tensor(
        np.asarray(data),
        dtype=torch.float32
    )


# ==========================================================
# TRAIN GAN
# ==========================================================

def train_gan(bars, genre, epochs=10):
    """
    Trains a small fully connected GAN on synthetic
    multi-track symbolic patterns.
    """

    training_data = create_training_data(
        bars=bars,
        genre=genre
    )

    output_size = training_data.shape[1]

    generator = MusicGenerator(output_size).to(DEVICE)

    discriminator = MusicDiscriminator(
        output_size
    ).to(DEVICE)

    dataset = TensorDataset(training_data)

    loader = DataLoader(
        dataset,
        batch_size=32,
        shuffle=True
    )

    generator_optimizer = torch.optim.Adam(
        generator.parameters(),
        lr=0.0002,
        betas=(0.5, 0.999)
    )

    discriminator_optimizer = torch.optim.Adam(
        discriminator.parameters(),
        lr=0.0002,
        betas=(0.5, 0.999)
    )

    loss_function = nn.BCEWithLogitsLoss()

    generator.train()
    discriminator.train()

    for epoch in range(epochs):
        total_g_loss = 0.0
        total_d_loss = 0.0
        batches = 0

        for (real_music,) in loader:
            real_music = real_music.to(DEVICE)
            batch_size = real_music.size(0)

            real_labels = torch.ones(
                batch_size, 1, device=DEVICE
            )

            fake_labels = torch.zeros(
                batch_size, 1, device=DEVICE
            )

            # ------------------------------------------
            # TRAIN DISCRIMINATOR
            # ------------------------------------------

            discriminator_optimizer.zero_grad()

            real_output = discriminator(real_music)

            real_loss = loss_function(
                real_output,
                real_labels
            )

            noise = torch.randn(
                batch_size,
                LATENT_SIZE,
                device=DEVICE
            )

            fake_music = generator(noise).detach()

            fake_output = discriminator(fake_music)

            fake_loss = loss_function(
                fake_output,
                fake_labels
            )

            discriminator_loss = (
                real_loss + fake_loss
            ) / 2

            discriminator_loss.backward()
            discriminator_optimizer.step()

            # ------------------------------------------
            # TRAIN GENERATOR
            # ------------------------------------------

            generator_optimizer.zero_grad()

            noise = torch.randn(
                batch_size,
                LATENT_SIZE,
                device=DEVICE
            )

            generated_music = generator(noise)

            generated_output = discriminator(
                generated_music
            )

            generator_loss = loss_function(
                generated_output,
                real_labels
            )

            generator_loss.backward()
            generator_optimizer.step()

            total_g_loss += generator_loss.item()
            total_d_loss += discriminator_loss.item()
            batches += 1

    generator.eval()

    return generator


# ==========================================================
# GENERATE FOUR-TRACK SYMBOLIC MUSIC
# ==========================================================

def generate_pattern(
    genre="Pop",
    bars=4,
    epochs=10,
    seed=None
):
    """
    Returns a binary symbolic pattern.

    Shape:
        (4, bars * 16, 12)

    Track order:
        0 = Piano
        1 = Bass
        2 = Melody
        3 = Drums
    """

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

    generator = train_gan(
        bars=bars,
        genre=genre,
        epochs=epochs
    )

    with torch.no_grad():
        noise = torch.randn(
            1,
            LATENT_SIZE,
            device=DEVICE
        )

        output = generator(noise)

        raw_pattern = output.cpu().numpy().reshape(
            4,
            bars * STEPS_PER_BAR,
            PITCH_CLASSES
        )

    pattern = np.zeros_like(
        raw_pattern,
        dtype=np.float32
    )

    # Threshold each track separately
    for track_index in range(4):
        track = raw_pattern[track_index]

        threshold = max(
            0.35,
            float(np.quantile(track, 0.88))
        )

        pattern[track_index] = (
            track >= threshold
        ).astype(np.float32)

    # Ensure the generated tracks are not completely empty.
    # Add simple fallback notes when the GAN generates none.
    for step in range(bars * STEPS_PER_BAR):
        if not pattern[0, step].any() and step % 4 == 0:
            pattern[0, step, 0] = 1.0

        if not pattern[1, step].any() and step % 8 == 0:
            pattern[1, step, 0] = 1.0

        if (
            not pattern[2, step].any()
            and step % 4 == 0
        ):
            pattern[2, step, 7] = 1.0

        if (
            not pattern[3, step].any()
            and step % 4 == 0
        ):
            pattern[3, step, 0 if step % 8 == 0 else 2] = 1.0

    return pattern


# ==========================================================
# CONVERT SYMBOLIC PATTERN TO MIDI
# ==========================================================

def create_midi(pattern, tempo=120):
    """
    Converts the generated pattern into a four-track MIDI.
    """

    midi = pretty_midi.PrettyMIDI(
        initial_tempo=tempo
    )

    instruments = [
        pretty_midi.Instrument(
            program=0,
            name="Piano"
        ),

        pretty_midi.Instrument(
            program=pretty_midi.instrument_name_to_program(
                "Electric Bass (finger)"
            ),
            name="Bass"
        ),

        pretty_midi.Instrument(
            program=pretty_midi.instrument_name_to_program(
                "Lead 1 (square)"
            ),
            name="Melody"
        ),

        pretty_midi.Instrument(
            program=0,
            is_drum=True,
            name="Drums"
        ),
    ]

    for track_index, instrument in enumerate(instruments):
        track_pattern = pattern[track_index]

        low, high = TRACK_RANGES[
            TRACK_NAMES[track_index]
        ]

        for step in range(track_pattern.shape[0]):
            for pitch_class in range(PITCH_CLASSES):
                if track_pattern[step, pitch_class] < 0.5:
                    continue

                if track_index == 3:
                    # General MIDI percussion pitches
                    drum_notes = [36, 38, 42, 46]

                    pitch = drum_notes[
                        pitch_class % len(drum_notes)
                    ]

                else:
                    candidates = [
                        pitch
                        for pitch in range(low, high + 1)
                        if pitch % 12 == pitch_class
                    ]

                    if not candidates:
                        continue

                    pitch = random.choice(candidates)

                # Sixteenth-note timing
                start = (
                    step * 60.0 / tempo / 4
                )

                duration = 60.0 / tempo / 4

                end = start + duration

                instrument.notes.append(
                    pretty_midi.Note(
                        velocity=random.randint(75, 110),
                        pitch=pitch,
                        start=start,
                        end=end
                    )
                )

        midi.instruments.append(instrument)

    return midi


# ==========================================================
# MAIN FUNCTION FOR STREAMLIT
# ==========================================================

def generate_music(
    genre="Pop",
    tempo=120,
    bars=4,
    epochs=10
):
    """
    Called by app.py.

    Returns:
        midi: PrettyMIDI object
        pattern: NumPy array of generated symbolic notes
    """

    pattern = generate_pattern(
        genre=genre,
        bars=bars,
        epochs=epochs
    )

    midi = create_midi(
        pattern=pattern,
        tempo=tempo
    )

    return midi, pattern
