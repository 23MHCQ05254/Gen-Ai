
import os
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras import layers, models
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.callbacks import EarlyStopping

MODEL_PATH = "cifar10_model.keras"
HISTORY_PATH = "training_history.npz"

CLASS_NAMES = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck"
]


def build_cnn_model():
    """Create a deep CNN for CIFAR-10 classification."""

    model = models.Sequential([
        layers.Input(shape=(32, 32, 3)),

        layers.Conv2D(32, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.Conv2D(32, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        layers.Dropout(0.25),

        layers.Conv2D(64, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.Conv2D(64, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        layers.Dropout(0.30),

        layers.Conv2D(128, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.Conv2D(128, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        layers.Dropout(0.35),

        layers.Flatten(),
        layers.Dense(128, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.40),
        layers.Dense(10, activation="softmax")
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


def train_model(epochs=10, batch_size=64):
    """Train the CNN and evaluate it on the CIFAR-10 test dataset."""

    (x_train, y_train), (x_test, y_test) = cifar10.load_data()

    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0

    y_train = y_train.reshape(-1)
    y_test = y_test.reshape(-1)

    model = build_cnn_model()

    early_stopping = EarlyStopping(
        monitor="val_loss",
        patience=3,
        restore_best_weights=True
    )

    history = model.fit(
        x_train,
        y_train,
        epochs=int(epochs),
        batch_size=int(batch_size),
        validation_split=0.1,
        callbacks=[early_stopping],
        verbose=1
    )

    test_loss, test_accuracy = model.evaluate(
        x_test, y_test, verbose=0
    )

    model.save(MODEL_PATH)

    np.savez(
        HISTORY_PATH,
        accuracy=np.array(history.history["accuracy"]),
        val_accuracy=np.array(history.history["val_accuracy"]),
        loss=np.array(history.history["loss"]),
        val_loss=np.array(history.history["val_loss"]),
        test_loss=np.array([test_loss]),
        test_accuracy=np.array([test_accuracy])
    )

    return {
        "model": model,
        "history": history.history,
        "test_loss": float(test_loss),
        "test_accuracy": float(test_accuracy),
        "epochs_completed": len(history.history["loss"])
    }


def load_trained_model():
    """Load the saved CNN model."""

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Model not found. Click Train CNN Model first."
        )

    return tf.keras.models.load_model(MODEL_PATH)


def predict_image(image_source, model=None):
    """Return predicted class, confidence, and probabilities."""

    image = Image.open(image_source).convert("RGB")
    image = image.resize((32, 32), Image.Resampling.BILINEAR)

    image_array = np.asarray(image, dtype=np.float32) / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    if model is None:
        model = load_trained_model()

    probabilities = model.predict(
        image_array, verbose=0
    )[0]

    predicted_index = int(np.argmax(probabilities))

    predicted_class = CLASS_NAMES[predicted_index]
    confidence = float(probabilities[predicted_index]) * 100

    return (
        predicted_class,
        confidence,
        probabilities.astype(float).tolist()
    )


def load_saved_evaluation():
    """Load saved accuracy and loss information."""

    if not os.path.exists(HISTORY_PATH):
        return None

    with np.load(HISTORY_PATH) as data:
        return {
            key: data[key].copy()
            for key in data.files
        }
