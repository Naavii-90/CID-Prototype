import streamlit as st
import os
from PIL import Image
import integrity_checker as ic
import face_detector as fd
import deepfake_detector as dd

#page configuration
st.set_page_config(page_title="DeepShield Prototype", layout="wide")

st.title(" DeepShield: Enhancing Media Integrity & Deepfake Detection")
st.write("Upload an image to verify its cryptographic and scan for AI alterations and manipulation")

#File upload interface
uploaded_file = st.file_uploader("Upload Media (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None: 
    #step 1: save the uploaded file temporarily so our previous scripts can read ir from the disk
    temp_file_path= "uploaded_temp.jpg"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("File uploaded successfully!")

    #split dashboard into two
    col1, col2 = st.columns(2)

    with col1: 
        st.subheader("1. Cryptographic Integrity")
        #run integrity_checker module
        file_hash = ic.generate_file_hash(temp_file_path)
        st.code(f"SHA-256 Hash:\n{file_hash}")
        st.info("In a live deployment, this hash is compared against a distributed ledger to verify origin")

        st.subheader("2. Media Preprocessing")
        #show the original uploaded image
        st.image(Image.open(temp_file_path), caption="Original Uploaded Media", use_container_width=True)

    with col2: 
        st.subheader("3. AI Analysis & Risk Scoring")

        #run the face_detector module
        with st.spinner("Scanning for facial regions..."):
            face_found = fd.detect_and_extract_face(temp_file_path)

        if face_found:
            #show the image with the green bounding box drawn by OpenCV
            st.image(Image.open("face_detection_result.jpg"), caption="Face Acquired", width=250)

            # run the deepfake_detector module
            with st.spinner("Running CNN Deepfake Engine..."):
                model = dd.build_cnn_architecture()
                score = dd.analyze_facial_media("extracted_face_for_CNN.jpg", model)

            #Display the final risk metrics
            st.metric(label="Deepfake Probability", value=f"{score:.2f}%")

            #The risk scoring logic
            if score > 70:
                st.error("🚨 HIGH RISK:Most Likely Deepfake Generated")
            elif score > 30:
                st.warning("⚠️ MEDIUM RISK:Slightly Suspicious Artifacts/Features Detected")
            else:
                st.success("✅ LOW RISK: Media Appears Authentic")
        else:
            st.warning("No faces detected in the uploaded image. CNN analysis bypassed.")