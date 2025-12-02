# smart_extractor.py - LangChain + FAISS Extraction

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
from field_config import INSURANCE_FORM_FIELDS, VALIDATION_RULES

class SmartExtractor:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.field_index = None
        self.field_mapping = []
        self._build_field_index()
    
    def _build_field_index(self):
        all_patterns = []
        
        for page_key, page_data in INSURANCE_FORM_FIELDS.items():
            for field in page_data["fields"]:
                for pattern in field["patterns"]:
                    all_patterns.append(pattern)
                    self.field_mapping.append({
                        "field_id": field["id"],
                        "name_en": field["name_en"],
                        "name_np": field["name_np"],
                        "validation": field["validation"],
                        "pattern": pattern
                    })
        
        embeddings = self.embedder.encode(all_patterns)
        dimension = embeddings.shape[1]
        self.field_index = faiss.IndexFlatL2(dimension)
        self.field_index.add(embeddings.astype('float32'))
    
    def find_matching_field(self, text, threshold=1.0):
        embedding = self.embedder.encode([text])
        distances, indices = self.field_index.search(embedding.astype('float32'), k=1)
        
        if distances[0][0] < threshold:
            return self.field_mapping[indices[0][0]]
        return None
    
    def extract_value(self, text, field_info):
        validation_type = field_info["validation"]
        pattern = VALIDATION_RULES.get(validation_type, r'.+')
        
        match = re.search(pattern, text)
        if match:
            return match.group(0)
        return text.strip()
    
    def process_ocr_results(self, ocr_results):
        extracted_fields = {}
        unmatched = []
        
        for item in ocr_results:
            text = item["text"]
            field_info = self.find_matching_field(text)
            
            if field_info:
                field_id = field_info["field_id"]
                value = self.extract_value(text, field_info)
                
                extracted_fields[field_id] = {
                    "field_name_en": field_info["name_en"],
                    "field_name_np": field_info["name_np"],
                    "raw_text": text,
                    "extracted_value": value,
                    "confidence": item.get("confidence", 0)
                }
            else:
                unmatched.append(text)
        
        return {
            "matched_fields": extracted_fields,
            "unmatched_text": unmatched
        }