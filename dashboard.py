import streamlit as st
from PIL import Image
import integrity_checker as ic
import face_detector as fd
import deepfake_detector as dd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="DeepShield", layout="wide", page_icon="🛡️")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #080810;
        color: #D8D8F0;
    }
    .stApp { background-color: #080810; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1280px; }

    /* ── Header ── */
    .ds-header {
        text-align: center;
        padding: 48px 0 36px;
    }
    .ds-header h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin: 0;
    }
    .ds-header h1 span { color: #00F5C4; }
    .ds-header p {
        font-size: 1rem;
        color: #6B6B90;
        margin-top: 8px;
    }

    /* ── Pipeline tracker ── */
    .pipeline {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        margin: 0 auto 40px;
        max-width: 640px;
    }
    .pipe-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
        flex: 1;
    }
    .pipe-dot {
        width: 36px; height: 36px;
        border-radius: 50%;
        border: 2px solid #252540;
        background: #12121F;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.85rem;
        color: #40405A;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
    }
    .pipe-dot.active {
        border-color: #00F5C4;
        color: #00F5C4;
        background: rgba(0,245,196,0.08);
        box-shadow: 0 0 12px rgba(0,245,196,0.25);
    }
    .pipe-label {
        font-size: 0.7rem;
        color: #40405A;
        font-family: 'Space Grotesk', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        text-align: center;
    }
    .pipe-label.active { color: #00F5C4; }
    .pipe-line {
        height: 2px;
        flex: 0.5;
        background: #252540;
        margin-bottom: 22px;
    }
    .pipe-line.active { background: #00F5C4; box-shadow: 0 0 6px rgba(0,245,196,0.4); }

    /* ── Upload zone ── */
    [data-testid="stFileUploader"] {
        background: #0E0E1C;
        border: 1.5px dashed #252540;
        border-radius: 14px;
        padding: 12px;
        transition: border-color 0.2s;
    }
    [data-testid="stFileUploader"]:hover { border-color: #00F5C4; }

    /* ── Section cards ── */
    .ds-card {
        background: #0E0E1C;
        border: 1px solid #1E1E35;
        border-radius: 16px;
        padding: 24px 22px 22px;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    .ds-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00F5C4, transparent);
        opacity: 0.5;
    }
    .ds-card-icon {
        font-size: 1.4rem;
        margin-bottom: 6px;
    }
    .ds-card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 4px;
    }
    .ds-card-badge {
        display: inline-block;
        font-size: 0.65rem;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 2px 8px;
        border-radius: 20px;
        background: rgba(0,245,196,0.1);
        color: #00F5C4;
        border: 1px solid rgba(0,245,196,0.2);
        margin-bottom: 10px;
    }
    .ds-card-desc {
        font-size: 0.82rem;
        color: #5A5A78;
        line-height: 1.55;
        margin-bottom: 16px;
    }
    .ds-divider {
        border: none;
        border-top: 1px solid #1E1E35;
        margin: 14px 0;
    }

    /* ── Hash display ── */
    .hash-box {
        background: #080810;
        border: 1px solid #1E1E35;
        border-radius: 10px;
        padding: 12px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #00F5C4;
        word-break: break-all;
        line-height: 1.6;
    }
    .hash-label {
        font-size: 0.65rem;
        font-family: 'Space Grotesk', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #40405A;
        margin-bottom: 6px;
    }

    /* ── Risk badges ── */
    .risk-high {
        background: rgba(255,69,96,0.12);
        border: 1px solid rgba(255,69,96,0.35);
        border-radius: 10px;
        padding: 14px 16px;
        color: #FF4560;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .risk-medium {
        background: rgba(255,171,0,0.1);
        border: 1px solid rgba(255,171,0,0.3);
        border-radius: 10px;
        padding: 14px 16px;
        color: #FFAB00;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .risk-low {
        background: rgba(0,227,150,0.1);
        border: 1px solid rgba(0,227,150,0.3);
        border-radius: 10px;
        padding: 14px 16px;
        color: #00E396;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .risk-score {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.4rem;
        font-weight: 600;
        display: block;
        margin-bottom: 4px;
    }

    /* ── Summary ── */
    .ds-summary {
        background: #0E0E1C;
        border: 1px solid #1E1E35;
        border-radius: 16px;
        padding: 28px 28px 24px;
        margin-top: 32px;
        position: relative;
    }
    .ds-summary::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #00F5C4, #7B61FF, #FF4560);
        border-radius: 16px 16px 0 0;
    }
    .ds-summary-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 20px;
    }
    .summary-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #14142A;
        font-size: 0.87rem;
    }
    .summary-row:last-child { border-bottom: none; }
    .summary-check { color: #6B6B90; }
    .summary-pass { color: #00E396; font-family: 'Space Grotesk', sans-serif; font-weight: 600; }
    .summary-warn { color: #FFAB00; font-family: 'Space Grotesk', sans-serif; font-weight: 600; }
    .summary-skip { color: #40405A; font-family: 'Space Grotesk', sans-serif; }

    /* ── Streamlit overrides ── */
    .stMetric { background: #12121F; border-radius: 10px; padding: 14px 16px; border: 1px solid #1E1E35; }
    .stMetric label { color: #5A5A78 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.06em; }
    .stMetric [data-testid="stMetricValue"] { color: #00F5C4 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 1.5rem !important; }
    div[data-testid="stSuccess"] { background: rgba(0,227,150,0.08); border: 1px solid rgba(0,227,150,0.25); border-radius: 10px; }
    div[data-testid="stInfo"] { background: rgba(0,180,255,0.07); border: 1px solid rgba(0,180,255,0.2); border-radius: 10px; }
    div[data-testid="stWarning"] { background: rgba(255,171,0,0.08); border: 1px solid rgba(255,171,0,0.2); border-radius: 10px; }
    div[data-testid="stError"] { background: rgba(255,69,96,0.08); border: 1px solid rgba(255,69,96,0.2); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ds-header">
    <h1>🛡️ Deep<span>Shield</span></h1>
    <p>Media Integrity Verification & Deepfake Detection — Prototype v0.1</p>
</div>
""", unsafe_allow_html=True)

# ── File Upload ───────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Drop an image to begin — JPG, JPEG, or PNG",
    type=["jpg", "png", "jpeg"],
    label_visibility="visible"
)

if uploaded_file is None:
    # ── Idle pipeline (all inactive) ──────────────────────────────────────────
    st.markdown("""
    <div class="pipeline">
        <div class="pipe-step"><div class="pipe-dot">1</div><div class="pipe-label">Hash</div></div>
        <div class="pipe-line"></div>
        <div class="pipe-step"><div class="pipe-dot">2</div><div class="pipe-label">Preview</div></div>
        <div class="pipe-line"></div>
        <div class="pipe-step"><div class="pipe-dot">3</div><div class="pipe-label">AI Scan</div></div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Save temp file ─────────────────────────────────────────────────────────
    temp_file_path = "uploaded_temp.jpg"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"**{uploaded_file.name}** loaded — pipeline running")

    # ── Active pipeline ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="pipeline">
        <div class="pipe-step"><div class="pipe-dot active">1</div><div class="pipe-label active">Hash</div></div>
        <div class="pipe-line active"></div>
        <div class="pipe-step"><div class="pipe-dot active">2</div><div class="pipe-label active">Preview</div></div>
        <div class="pipe-line active"></div>
        <div class="pipe-step"><div class="pipe-dot active">3</div><div class="pipe-label active">AI Scan</div></div>
    </div>
    """, unsafe_allow_html=True)

    results = {}
    col1, col2, col3 = st.columns(3, gap="medium")

    # ── Section 1: Cryptographic Integrity ────────────────────────────────────
    with col1:
        st.markdown('<div class="ds-card">', unsafe_allow_html=True)
        st.markdown("""
            <div class="ds-card-icon">🔐</div>
            <div class="ds-card-title">Cryptographic Integrity</div>
            <div class="ds-card-badge">SECTION 01</div>
            <div class="ds-card-desc">
                Generates a SHA-256 fingerprint of the uploaded file's raw bytes. 
                In production, this hash is cross-checked against a distributed ledger 
                to verify origin and detect any byte-level tampering.
            </div>
            <hr class="ds-divider">
        """, unsafe_allow_html=True)

        file_hash = ic.generate_file_hash(temp_file_path)
        st.markdown(f"""
            <div class="hash-label">SHA-256 Fingerprint</div>
            <div class="hash-box">{file_hash}</div>
        """, unsafe_allow_html=True)

        st.info("Ledger verification would run here in a live deployment.")
        results["hash"] = file_hash
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Section 2: Media Preview ───────────────────────────────────────────────
    with col2:
        st.markdown('<div class="ds-card">', unsafe_allow_html=True)
        st.markdown("""
            <div class="ds-card-icon">🖼️</div>
            <div class="ds-card-title">Media Preview</div>
            <div class="ds-card-badge">SECTION 02</div>
            <div class="ds-card-desc">
                Raw input as uploaded — no preprocessing applied. 
                This is what gets passed into the face detection and 
                CNN analysis pipeline downstream.
            </div>
            <hr class="ds-divider">
        """, unsafe_allow_html=True)

        st.image(Image.open(temp_file_path), caption="Original — unmodified", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Section 3: AI Analysis ─────────────────────────────────────────────────
    with col3:
        st.markdown('<div class="ds-card">', unsafe_allow_html=True)
        st.markdown("""
            <div class="ds-card-icon">🤖</div>
            <div class="ds-card-title">AI Analysis & Risk Scoring</div>
            <div class="ds-card-badge">SECTION 03</div>
            <div class="ds-card-desc">
                Face detection isolates facial regions, which are then classified 
                by a CNN-based deepfake engine. Output is a 0–100% probability 
                score indicating likelihood of AI manipulation.
            </div>
            <hr class="ds-divider">
        """, unsafe_allow_html=True)

        with st.spinner("Scanning for facial regions..."):
            face_found = fd.detect_and_extract_face(temp_file_path)

        if face_found:
            st.image(Image.open("face_detection_result.jpg"), caption="Detected face region", width=200)

            with st.spinner("Running CNN deepfake engine..."):
                model = dd.build_cnn_architecture()
                score = dd.analyze_facial_media("extracted_face_for_CNN.jpg", model)

            if score > 75:
                risk_level = "HIGH"
                st.markdown(f"""
                <div class="risk-high">
                    <span class="risk-score">{score:.1f}%</span>
                    🚨 HIGH RISK — Most likely deepfake generated
                </div>""", unsafe_allow_html=True)
            elif score > 45:
                risk_level = "MEDIUM"
                st.markdown(f"""
                <div class="risk-medium">
                    <span class="risk-score">{score:.1f}%</span>
                    ⚠️ MEDIUM RISK — Suspicious artifacts detected
                </div>""", unsafe_allow_html=True)
            else:
                risk_level = "LOW"
                st.markdown(f"""
                <div class="risk-low">
                    <span class="risk-score">{score:.1f}%</span>
                    ✅ LOW RISK — Media appears authentic
                </div>""", unsafe_allow_html=True)

            results.update({"face_found": True, "score": score, "risk": risk_level})
        else:
            st.warning("No faces detected — CNN analysis bypassed.")
            results.update({"face_found": False, "score": None, "risk": "N/A"})

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Summary ────────────────────────────────────────────────────────────────
    score_str = f"{results['score']:.1f}%" if results["score"] is not None else "—"
    face_str = "Detected" if results["face_found"] else "Not found"
    risk_str = results["risk"]

    cnn_result = (
        f'<span class="summary-pass">✅ Completed — {risk_str} RISK</span>'
        if results["face_found"] else
        '<span class="summary-skip">⏭ Skipped (no face)</span>'
    )
    face_class = "summary-pass" if results["face_found"] else "summary-warn"

    st.markdown(f"""
    <div class="ds-summary">
        <div class="ds-summary-title">📋 Analysis Summary — {uploaded_file.name}</div>
        <div class="summary-row">
            <span class="summary-check">🔐 SHA-256 hash generated</span>
            <span class="summary-pass">✅ Done</span>
        </div>
        <div class="summary-row">
            <span class="summary-check">🖼️ Media preview loaded</span>
            <span class="summary-pass">✅ Done</span>
        </div>
        <div class="summary-row">
            <span class="summary-check">👤 Face detection</span>
            <span class="{face_class}">{'✅ ' + face_str if results['face_found'] else '⚠️ ' + face_str}</span>
        </div>
        <div class="summary-row">
            <span class="summary-check">🤖 CNN deepfake analysis</span>
            {cnn_result}
        </div>
        <div class="summary-row">
            <span class="summary-check">📊 Deepfake probability score</span>
            <span class="summary-pass">{score_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)