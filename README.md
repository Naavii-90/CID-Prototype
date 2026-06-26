# DeepShield: Deepfake Detection System
An academic prototype built with Streamlit, OpenCV, and TensorFlow (MobileNetV2).

## Overview
DeepShield is a lightweight CNN pipeline designed to extract facial data from uploaded media and analyze texture variances to detect StyleGAN3 AI-generated artifacts.

## Requirements
* Python 3.9+
* TensorFlow / Keras 3
* OpenCV (`opencv-python`)
* Streamlit

## Quick Start
1. Clone this repository to your local machine.
2. Create and activate a virtual environment (_venv_) to run the prototype
3. Install the required dependencies from the text file:
   ```cmd
   pip install -r requirements.txt
4. Launch the DeepShield streamlit dashboard
   ```cmd
    python -m streamlit run dashboard.py