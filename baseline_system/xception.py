import cv2
import numpy as np
import time

def predict(image_path):
    """
    Xception-style baseline (higher complexity proxy model)
    """

    start = time.time()

    img = cv2.imread(image_path)
    if img is None:
        return "real", 0.0, 0

    img = cv2.resize(img, (128, 128))
    img = img / 255.0

    # Deeper feature simulation: channel variance + edge sensitivity
    edges = cv2.Canny((img * 255).astype(np.uint8), 100, 200)
    edge_score = np.mean(edges) / 255.0

    color_variance = np.var(img)

    score = (edge_score * 0.6) + (color_variance * 0.4)

    prob_fake = min(max(score * 3, 0), 1)

    label = "fake" if prob_fake > 0.5 else "real"

    latency = (time.time() - start) * 1000

    return label, prob_fake, latency
