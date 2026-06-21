import cv2
import numpy as np
import time

def predict(image_path):
    """
    MesoNet-style lightweight baseline detector (proxy implementation)
    Returns: label (real/fake), confidence score, latency
    """

    start = time.time()

    img = cv2.imread(image_path)
    if img is None:
        return "real", 0.0, 0

    img = cv2.resize(img, (128, 128))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Texture-based heuristic (simulates mesoscopic feature detection)
    score = np.std(img) / 255.0

    # Normalize to probability
    prob_fake = min(max(score * 2, 0), 1)

    label = "fake" if prob_fake > 0.5 else "real"

    latency = (time.time() - start) * 1000

    return label, prob_fake, latency
