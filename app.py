import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from textblob import TextBlob

st.title("📄 PDF Tilted Text Corrector with Agentic AI Agent")

uploaded_file = st.file_uploader("Upload a PDF", type=[".pdf"])

def extract_with_pymupdf(doc):
    text = ""
    tilted_words = []
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    span_text = span.get("text", "").strip()
                    if not span_text:
                        continue
                    bbox = span["bbox"]
                    # Detect tilt via bbox height/width ratio (simple heuristic)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    if h > w * 1.5:  # looks rotated/tilted
                        tilted_words.append(span_text)
                    text += " " + span_text
    return text.strip(), tilted_words

def extract_with_ocr(page):
    pix = page.get_pixmap()
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img)

def method4_correction(text):
    blob = TextBlob(text)
    return str(blob.correct())

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    outputs = []

    # Method 1 - PyMuPDF
    try:
        text, tilted = extract_with_pymupdf(doc)
        outputs.append(("PyMuPDF", text))
        st.subheader("Method 1: PyMuPDF Extraction")
        st.write(text)
        st.write("🌀 Tilted words (detected):", tilted)
    except Exception as e:
        outputs.append(("PyMuPDF", f"Failed: {e}"))

    # Method 2 - OCR
    try:
        page = doc[0]
        ocr_text = extract_with_ocr(page)
        outputs.append(("OCR", ocr_text))
        st.subheader("Method 2: OCR Extraction")
        st.write(ocr_text)
    except Exception as e:
        outputs.append(("OCR", f"Failed: {e}"))

    # Method 3 - Combine best
    final_text = ""
    for name, out in outputs:
        if out and not out.startswith("Failed"):
            final_text += " " + out
    final_text = final_text.strip()

    # Method 4 - Correction
    if final_text:
        corrected = method4_correction(final_text)
        st.subheader("✅ Final Corrected Sentence")
        st.write(corrected)

        # =======================
        # 🤖 Agentic AI Agent
        # =======================
        st.subheader("🤖 Agentic AI Agent: Input vs Corrected Comparison")

        import difflib
        raw_text = outputs[0][1] if outputs else ""

        if raw_text:
            diff = difflib.ndiff(raw_text.split(), corrected.split())
            added, removed, same = [], [], []
            for d in diff:
                if d.startswith("+ "):
                    added.append(d[2:])
                elif d.startswith("- "):
                    removed.append(d[2:])
                else:
                    same.append(d[2:])

            st.write("🔍 **Same words:**", " ".join(same))
            st.write("➕ **Added/Corrected:**", " ".join(added))
            st.write("❌ **Removed/Incorrect:**", " ".join(removed))

            seq = difflib.SequenceMatcher(None, raw_text, corrected)
            score = round(seq.ratio() * 100, 2)
            st.write(f"📊 **Match Score:** {score}%")
