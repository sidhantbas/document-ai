# app.py - Production Document AI

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

st.set_page_config(page_title="Document AI Pro", page_icon="🧠", layout="wide")

if "extractions" not in st.session_state:
    st.session_state.extractions = {}

tm = TemplateManager()

with st.sidebar:
    st.header("Document AI Pro")
    st.caption("Dynamic | Accurate | Free")
    
    st.divider()
    
    st.subheader("Templates")
    templates = tm.list_templates()
    for t in templates:
        st.caption(f"• {t}")
    
    with st.expander("+ New Template"):
        name = st.text_input("Name", key="tpl_name")
        fields = st.text_area("Fields JSON", key="tpl_fields", height=150)
        if st.button("Save"):
            try:
                tm.save_template(name, json.loads(fields))
                st.success("Saved!")
                st.rerun()
            except:
                st.error("Invalid JSON")
    
    st.divider()
    
    st.subheader("Processed")
    if st.session_state.extractions:
        for doc in st.session_state.extractions.keys():
            st.caption(f"Done: {doc}")
        
        if st.button("Export All (Excel)"):
            excel = Exporter.batch_to_excel(st.session_state.extractions)
            st.download_button("Download", excel, "batch_export.xlsx")
        
        if st.button("Clear History"):
            st.session_state.extractions = {}
            st.rerun()

tab1, tab2 = st.tabs(["Extract", "Verify"])

with tab1:
    st.header("Extract Documents")
    
    uploaded = st.file_uploader("Upload", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if uploaded:
        c1, c2, c3 = st.columns(3)
        template_choice = c1.selectbox("Template", ["Auto"] + tm.list_templates())
        confidence = c2.slider("Confidence", 0.0, 1.0, 0.25)
        all_pages = c3.checkbox("All pages", value=True)
        
        if st.button("Process All", type="primary"):
            reader = load_ocr()
            
            progress = st.progress(0)
            
            for idx, file in enumerate(uploaded):
                progress.progress((idx + 1) / len(uploaded))
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
                    st.warning(f"{file.name}: No template matched")
            
            st.success("Done!")
        
        if st.session_state.extractions:
            st.divider()
            
            for doc_name, extracted in st.session_state.extractions.items():
                with st.expander(f"Doc: {doc_name}"):
                    cols = st.columns(2)
                    
                    for i, (field, data) in enumerate(extracted.items()):
                        cols[i % 2].text_input(field, data.get("value", ""), key=f"{doc_name}_{field}")
                    
                    bc1, bc2, bc3 = st.columns(3)
                    bc1.download_button("JSON", Exporter.to_json(extracted), f"{doc_name}.json")
                    bc2.download_button("CSV", Exporter.to_csv(extracted), f"{doc_name}.csv")
                    bc3.download_button("Excel", Exporter.to_excel(extracted), f"{doc_name}.xlsx")

with tab2:
    st.header("Verify Extractions")
    
    if not st.session_state.extractions:
        st.info("Process documents first")
    else:
        doc_choice = st.selectbox("Select Document", list(st.session_state.extractions.keys()))
        
        if doc_choice:
            extracted = st.session_state.extractions[doc_choice]
            
            if st.button("Run Verification", type="primary"):
                results = Verifier.run_all_checks(extracted)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Passed", results["passed"])
                col2.metric("Failed", results["failed"])
                col3.metric("Score", results["score"])
                
                st.divider()
                
                for check in results["checks"]:
                    field = check.get("field", "Unknown")
                    valid = check.get("valid", False)
                    
                    if valid:
                        st.success(f"Pass: {field}")
                    else:
                        error = check.get("error", "Failed")
                        st.error(f"Fail: {field} - {error}")