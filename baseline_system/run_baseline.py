import os
import cv2
import time
import numpy as np
import pandas as pd

# -----------------------------
# Simple Baseline Detector
# (MesoNet-style placeholder logic)
# -----------------------------

def predict(image_path):
    """
    Baseline fake/real predictor (simple CNN-like heuristic)
    Replace later with real MesoNet model if needed.
    """
    img = cv2.imread(image_path)

    if img is None:
        return None, 0

    img = cv2.resize(img, (128, 128))
    img = img / 255.0

    # Simple heuristic score (acts like probability)
    score = np.mean(img) * 100

    label = "fake" if score > 50 else "real"

    return label, score


# -----------------------------
# Evaluation Function
# -----------------------------

def evaluate(dataset_path="dataset"):
    results = []

    total = 0
    correct = 0

    confusion = {
        "tp": 0, "tn": 0,
        "fp": 0, "fn": 0
    }

    start_all = time.time()

    for true_label in ["real", "fake"]:
        folder = os.path.join(dataset_path, true_label)

        for file in os.listdir(folder):
            path = os.path.join(folder, file)

            start = time.time()
            pred_label, score = predict(path)
            end = time.time()

            if pred_label is None:
                continue

            total += 1

            # accuracy check
            if pred_label == true_label:
                correct += 1

            # confusion matrix
            if true_label == "fake" and pred_label == "fake":
                confusion["tp"] += 1
            elif true_label == "real" and pred_label == "real":
                confusion["tn"] += 1
            elif true_label == "real" and pred_label == "fake":
                confusion["fp"] += 1
            elif true_label == "fake" and pred_label == "real":
                confusion["fn"] += 1

            results.append({
                "file": file,
                "true": true_label,
                "pred": pred_label,
                "score": round(score, 2),
                "time_ms": round((end - start) * 1000, 2)
            })

    end_all = time.time()

    accuracy = (correct / total) * 100 if total > 0 else 0
    avg_latency = np.mean([r["time_ms"] for r in results])

    # -----------------------------
    # Print Results
    # -----------------------------
    print("\n===== BASELINE SYSTEM RESULTS =====")
    print(f"Total Images: {total}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Average Latency: {avg_latency:.2f} ms")
    print("\nConfusion Matrix:")
    print(confusion)

    # -----------------------------
    # Save results for report
    # -----------------------------
    df = pd.DataFrame(results)
    df.to_csv("baseline_results.csv", index=False)

    print("\nResults saved to baseline_results.csv")


# -----------------------------
# Run
# -----------------------------

if __name__ == "__main__":
    evaluate()
