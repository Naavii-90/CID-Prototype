import os
import pandas as pd

from baselines import mesonet
from baselines import xception

# import your DeepShield function
from deepshield.deepfake_detector import analyze_facial_media

DATASET = "dataset"

results = []

# ----------------------------
# DeepShield wrapper
# ----------------------------
def predict_deepshield(image_path):
    score = analyze_facial_media(image_path, None)

    if score is None:
        return "real", 0.0, 0

    label = "fake" if score > 50 else "real"
    return label, score, 100  # approx latency placeholder


# ----------------------------
# Run experiment
# ----------------------------
def run_model(model_name, predict_func):
    for label in ["real", "fake"]:
        folder = os.path.join(DATASET, label)

        for file in os.listdir(folder):
            path = os.path.join(folder, file)

            pred, score, latency = predict_func(path)

            results.append({
                "model": model_name,
                "file": file,
                "true": label,
                "pred": pred,
                "score": score,
                "latency_ms": latency
            })


# ----------------------------
# Execute all models
# ----------------------------
run_model("DeepShield", predict_deepshield)
run_model("MesoNet", mesonet.predict)
run_model("XceptionNet", xception.predict)


# ----------------------------
# Save results
# ----------------------------
df = pd.DataFrame(results)
df.to_csv("results/all_results.csv", index=False)

print("Experiment completed!")
print(df.head())
