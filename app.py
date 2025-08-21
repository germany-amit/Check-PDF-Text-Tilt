import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from textblob import TextBlob
import io

st.title("📄 Tilted Text Corrector (FMEA Safety MVP)")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

def method1_pymupdf(doc):
    """Extract text directly using PyMuPDF"""
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text.strip()

def method2_bbox_rotation(doc):
    """Detect tilted words using bounding boxes + orientation"""
    tilted = []
    normal = []
    for pnum, page in enumerate(doc, 1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        txt = s.get("text", "").strip()
                        if not txt:
                            continue
                        dir_vec = tuple(round(x, 2) for x in s.get("dir", (1, 0)))
                        if dir_vec not in [(1, 0), (0, 1)]:
                            tilted.append((pnum, txt, dir_vec))
                        else:
                            normal.append(txt)
    return " ".join(normal + [w for _, w, _ in tilted])

def method3_ocr(doc):
    """Fallback OCR via pytesseract"""
    text = ""
    for page in doc:
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text += pytesseract.image_to_string(img) + "\n"
    return text.strip()

def method4_correction(text):
    """Spell & grammar correction"""
    return str(TextBlob(text).correct())

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    st.subheader("🛠 Multi-Strategy Results (FMEA Safety Factor)")
    outputs = []

    # Strategy 1
    try:
        out1 = method1_pymupdf(doc)
        if out1:
            outputs.append(("Method 1 (Direct Extract)", out1))
    except Exception as e:
        pass

    # Strategy 2
    try:
        out2 = method2_bbox_rotation(doc)
        if out2:
            outputs.append(("Method 2 (BBox Tilt Check)", out2))
    except Exception as e:
        pass

    # Strategy 3
    try:
        out3 = method3_ocr(doc)
        if out3:
            outputs.append(("Method 3 (OCR)", out3))
    except Exception as e:
        pass

    # Pick first non-empty result
    final_text = ""
    if outputs:
        for label, text in outputs:
            st.write(f"**{label}:** {text}")
