"""
DeepShield - Model Training Script

Trains the deepfake-detection head on top of a frozen, pretrained MobileNetV2
backbone (transfer learning). We use transfer learning instead of training a
CNN from scratch because our dataset is tiny (100 images total) -- a
from-scratch CNN would badly overfit on that little data. MobileNetV2 has
already learned general visual features (edges, textures, shapes) from
millions of images, so we only need to train a small classifier head on top
of those features for our specific real-vs-fake task.

Run this once to produce 'deepshield_trained_weights.h5', which
deepfake_detector.py then loads at runtime.
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import numpy as np
from pathlib import Path

IMG_SIZE = (128, 128)
BATCH_SIZE = 8          # small on purpose - we only have 100 images total
EPOCHS = 20
DATASET_DIR = "dataset"
WEIGHTS_OUT = "deepshield_trained_weights.weights.h5"

# Label convention: 0 = real, 1 = fake.
# This matches deepfake_detector.py, where a HIGHER score means MORE likely fake.


def load_dataset():
    """
    Loads images from dataset/real and dataset/fake, resizes them, and
    returns (train_ds, val_ds) as tf.data.Dataset objects with an 80/20 split.
    """
    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        labels="inferred",
        label_mode="binary",
        class_names=["real", "fake"],  # forces real=0, fake=1
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        subset="training",
        seed=42,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        labels="inferred",
        label_mode="binary",
        class_names=["real", "fake"],
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        subset="validation",
        seed=42,
    )
    return train_ds, val_ds


def build_augmentation():
    """
    Light data augmentation. With only 100 images, augmentation helps the
    model see a bit more variety instead of memorising the exact 100 photos.
    """
    return tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.08),
        tf.keras.layers.RandomZoom(0.1),
        tf.keras.layers.RandomContrast(0.1),
    ])


def build_transfer_model():
    """
    Builds the MobileNetV2-based model:
      pretrained MobileNetV2 (frozen) -> pooling -> small dense head -> sigmoid

    IMPORTANT: this architecture must exactly match build_cnn_architecture()
    in deepfake_detector.py, since that's what loads these saved weights.
    """
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False  # freeze the pretrained backbone

    inputs = tf.keras.Input(shape=(IMG_SIZE[0], IMG_SIZE[1], 3))
    x = build_augmentation()(inputs)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x * 255.0)
    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main():
    print("=== DeepShield: Model Training ===\n")

    if not Path(DATASET_DIR).exists():
        print(f"[!] Error: '{DATASET_DIR}' folder not found. "
              f"Expected dataset/real/ and dataset/fake/ subfolders.")
        return

    print("[*] Loading dataset...")
    train_ds, val_ds = load_dataset()

    # Normalize pixel values to [0,1] (preprocess_input above then rescales
    # for MobileNetV2's expected range internally)
    normalize = tf.keras.layers.Rescaling(1.0 / 255)
    train_ds = train_ds.map(lambda x, y: (normalize(x), y))
    val_ds = val_ds.map(lambda x, y: (normalize(x), y))

    train_ds = train_ds.cache().prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.cache().prefetch(tf.data.AUTOTUNE)

    print("[*] Building MobileNetV2 transfer-learning model...")
    model = build_transfer_model()
    model.summary()

    print("\n[*] Training...\n")
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=5, restore_best_weights=True
    )
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=[early_stop],
    )

    val_loss, val_acc = model.evaluate(val_ds, verbose=0)
    print(f"\n[+] Final validation accuracy: {val_acc*100:.1f}%")
    print(f"[+] Final validation loss:     {val_loss:.4f}")

    print(
        "\n[!] Honest caveat: this model was trained on only 100 images "
        "(50 real / 50 fake). That's enough to prove the pipeline actually "
        "learns something real, but it is NOT enough data for a reliable, "
        "production-grade deepfake detector."
    )

    model.save_weights(WEIGHTS_OUT)
    print(f"\n[+] Saved trained weights to '{WEIGHTS_OUT}'")


if __name__ == "__main__":
    main()
