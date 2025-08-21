import streamlit as st
import fitz  # PyMuPDF

st.title("📄 Tilted Text Detector MVP")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    tilted_words = []
    normal_words = []

    for page_num, page in enumerate(doc, start=1):
        words = page.get_text("rawdict")["blocks"]
        for block in words:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        angle = span.get("dir", (1, 0))  # direction vector
                        # if rotated, vector will differ from (1,0)
                        if angle not in [(1, 0), (0, 1)]:
                            tilted_words.append((page_num, text, angle))
                        else:
                            normal_words.append(text)

    st.subheader("✅ Extracted Text")
    st.write(" ".join(normal_words))

    st.subheader("⚠️ Tilted Words Found")
    if tilted_words:
        for pg, word, ang in tilted_words:
            st.write(f"Page {pg}: '{word}' → Tilt detected (direction={ang})")
    else:
        st.write("No tilted words detected.")
