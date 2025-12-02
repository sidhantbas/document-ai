import streamlit as st
from PIL import Image
import fitz
import json
import ssl
import numpy as np

ssl._create_default_https_context = ssl._create_unverified_context

import easyocr
from template_manager import TemplateManager
from ocr_processor import OCRProcessor
from verifier import Verifier
from exporter import Exporter

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en', 'ne'], gpu=False)

def pdf_to_images(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images

def ocr_image(reader, image):
    results = reader.readtext(np.array(image))
    return [{"text": t, "confidence": c, "bbox": b} for b, t, c in results]

st.set_page_config(page_title="Document AI", page_icon="📄", layout="wide")

if "extractions" not in st.session_state:
    st.session_state.extractions = {}

tm = TemplateManager()

with st.sidebar:
    st.header("Document AI")
    templates = tm.list_templates()
    for t in templates:
        st.caption(t)
    
    with st.expander("New Template"):
        name = st.text_input("Name", key="tpl_name")
        fields = st.text_area("Fields JSON", key="tpl_fields")
        if st.button("Save"):
            try:
                tm.save_template(name, json.loads(fields))
                st.success("Saved")
                st.rerun()
            except:
                st.error("Invalid JSON")

tab1, tab2 = st.tabs(["Extract", "Verify"])

with tab1:
    st.header("Extract Documents")
    uploaded = st.file_uploader("Upload", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if uploaded:
        c1, c2 = st.columns(2)
        template_choice = c1.selectbox("Template", ["Auto"] + tm.list_templates())
        confidence = c2.slider("Confidence", 0.0, 1.0, 0.25)
        
        if st.button("Process", type="primary"):
            reader = load_ocr()
            
            for file in uploaded:
                st.write(f"Processing: {file.name}")
                
                if file.type == "application/pdf":
                    images = pdf_to_images(file.read())
                else:
                    images = [Image.open(file)]
                
                all_ocr = []
                for img in images:
                    results = ocr_image(reader, img)
                    for r in results:
                        if r["confidence"] >= confidence:
                            all_ocr.append(r)
                
                tpl = template_choice
                if tpl == "Auto":
                    texts = [r["text"] for r in all_ocr]
                    tpl = tm.auto_detect_template(texts) or ""
                
                template = tm.get_template(tpl)
                if template:
                    extracted = OCRProcessor.process_results(all_ocr, template["fields"])
                    st.session_state.extractions[file.name] = extracted
                    st.success(f"{file.name}: {len(extracted)} fields")
                else:
                    st.warning(f"{file.name}: No template")
            
            st.success("Done")
        
        if st.session_state.extractions:
            for doc_name, extracted in st.session_state.extractions.items():
                with st.expander(doc_name):
                    for field, data in extracted.items():
                        st.text_input(field, data.get("value", ""), key=f"{doc_name}_{field}")
                    
                    st.download_button("JSON", Exporter.to_json(extracted), f"{doc_name}.json")

with tab2:
    st.header("Verify")
    if not st.session_state.extractions:
        st.info("Process documents first")
    else:
        doc_choice = st.selectbox("Document", list(st.session_state.extractions.keys()))
        if doc_choice and st.button("Verify", type="primary"):
            results = Verifier.run_all_checks(st.session_state.extractions[doc_choice])
            st.metric("Score", results["score"])
            for check in results["checks"]:
                if check.get("valid"):
                    st.success(f"Pass: {check['field']}")
                else:
                    st.error(f"Fail: {check['field']}")