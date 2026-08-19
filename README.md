# DeepShield: Deepfake Detection System
An academic group prototype built with Streamlit, OpenCV, and TensorFlow (MobileNetV2 transfer learning).

## Overview
DeepShield is a media-integrity pipeline with three stages:
1. **Cryptographic integrity check** — generates a SHA-256 hash of the uploaded file for tamper detection.
2. **Face detection** — uses OpenCV's Haar Cascade classifier to locate and extract the facial region.
3. **Deepfake classification** — the extracted face is passed through a CNN built on a frozen, ImageNet-pretrained MobileNetV2 backbone with a custom trained classification head, producing a real/fake probability score.

All three stages are tied together in a Streamlit dashboard (`dashboard.py`).

## My contribution
I built the basics of the CNN architecture and training pipeline (deepfake_detector.py, train_model.py) and the face detection module (face_detector.py)and the integrity_checker.py. While my teammate helped with the dashboard.py GUI.

## Model training & an honest limitation
The classifier is trained via transfer learning (`train_model.py`) rather than from scratch, since our dataset is very small (100 images: 50 real / 50 fake). Transfer learning lets us reuse MobileNetV2's features learned from millions of images and only train a small head on top, which is far more realistic than training a full CNN from 100 images (which would badly overfit).

**Limitation:** 100 images is enough to prove the pipeline learns a real signal, but it is **not** enough data for a production-grade or generalizable deepfake detector. Validation accuracy from training is printed at the end of `train_model.py`.

**Generalization test:** validation accuracy during training reached 100% (validation loss 0.0130), but this was measured on a held-out split of the *same* 100-image dataset (~20 images), which is too small a sample to be a meaningful accuracy claim on its own. To sanity-check this, I ran the trained model on new images from outside the training dataset (real photos + AI-generated faces from a different source). Results were inconsistent — some AI-generated images were correctly flagged, but others scored as low as ~1% ("real") despite being fully synthetic. This indicates the model likely picked up on dataset-specific artifacts (e.g. resolution, compression, or source-specific visual patterns common to the training images) rather than learning generalizable deepfake signatures/artifacts — a known failure mode called 'shortcut learning', common with small, single-source datasets. The 100% training-validation figure should not be read as real-world accuracy; it reflects fit to this specific dataset only.

## Requirements
* Python 3.9+
* TensorFlow / Keras 3
* OpenCV (`opencv-python`)
* Streamlit

## Quick Start
1. Clone this repository to your local machine.
2. Create and activate a virtual environment (_venv_) to run the prototype.
3. Install the required dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
4. Train the model (produces `deepshield_trained_weights.h5`, required before running the dashboard):
   ```cmd
   python train_model.py
   ```
5. Launch the DeepShield Streamlit dashboard:
   ```cmd
   python -m streamlit run dashboard.py
   ```

## Project structure
| File | Role |
|---|---|
| `integrity_checker.py` | SHA-256 hashing for tamper detection |
| `face_detector.py` | Haar Cascade face detection & extraction |
| `deepfake_detector.py` | MobileNetV2-based CNN, loads trained weights, runs inference |
| `train_model.py` | Trains the classifier head on `dataset/real` and `dataset/fake` |
| `dashboard.py` | Streamlit UI tying the pipeline together |

## Future improvements
- Train on a larger, multi-source dataset (e.g. FaceForensics++) to reduce shortcut learning and improve generalization
- Add cross-validation instead of a single train/val split, given the small dataset size
- Evaluate on a proper external test set, not just spot-checked images