# Vision script for classification

import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps

_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models/keras_model.h5")
_model      = None   # loaded on first use
class_names = ["leeg", "blauw", "geel", "groen", "roze"]

def _get_model():
    """Load (or return cached) Keras model."""
    global _model
    if _model is None:
        print("Loading classification model...")
        _model = tf.keras.models.load_model(_MODEL_PATH, compile=False)
        print("Classification model loaded.\n")
    return _model

########### Module API ###########

def classify_frame(frame):
    """
    Classify a BGR OpenCV frame captured directly from the camera.
    Returns (class_name, confidence) where class_name is one of:
      'leeg', 'blauw', 'geel', 'groen', 'roze'
    """
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb)
    image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)

    data       = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0]    = (np.asarray(image).astype(np.float32) / 127.5) - 1

    prediction = _get_model().predict(data, verbose=0)
    index      = int(np.argmax(prediction))
    return class_names[index], float(prediction[0][index])

########### Standalone (file-based) ###########

def voorspel_afbeelding(afbeelding_pad):
    """Classify an image file and print detailed results (standalone use)."""
    image = Image.open(afbeelding_pad).convert("RGB")
    image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)

    data    = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = (np.asarray(image).astype(np.float32) / 127.5) - 1

    prediction = _get_model().predict(data, verbose=0)
    index      = int(np.argmax(prediction))
    class_name = class_names[index]
    confidence = prediction[0][index]

    print(f"\nResultaat voor '{afbeelding_pad}':")
    print(f"Beste match: {class_name}")
    print(f"Zekerheid: {confidence * 100:.2f}%")
    print("\nAlle scores:")
    for i, score in enumerate(prediction[0]):
        print(f"- {class_names[i]}: {score * 100:.2f}%")

if __name__ == "__main__":
    bestandsnaam = "test.jpeg"
    if os.path.exists(bestandsnaam):
        voorspel_afbeelding(bestandsnaam)
    else:
        print(f"Zet eerst een afbeelding met de naam '{bestandsnaam}' in deze map om te testen!")