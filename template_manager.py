# template_manager.py - Dynamic Template Learning
# ================================================

import json
import os
from rapidfuzz import fuzz, process

TEMPLATE_DIR = "templates"

class TemplateManager:
    def __init__(self):
        os.makedirs(TEMPLATE_DIR, exist_ok=True)
        self.templates = {}
        self.load_all_templates()
    
    def load_all_templates(self):
        """Load all saved templates"""
        self.templates = {}
        for file in os.listdir(TEMPLATE_DIR):
            if file.endswith('.json'):
                name = file.replace('.json', '')
                with open(f"{TEMPLATE_DIR}/{file}", 'r', encoding='utf-8') as f:
                    self.templates[name] = json.load(f)
    
    def save_template(self, name, fields):
        """Save a new template"""
        template = {
            "name": name,
            "fields": fields
        }
        with open(f"{TEMPLATE_DIR}/{name}.json", 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        self.templates[name] = template
    
    def get_template(self, name):
        """Get template by name"""
        return self.templates.get(name)
    
    def list_templates(self):
        """List all template names"""
        return list(self.templates.keys())
    
    def match_field(self, text, template_name, threshold=70):
        """Match text to a field in template using fuzzy matching"""
        template = self.templates.get(template_name)
        if not template:
            return None
        
        all_labels = []
        label_to_field = {}
        
        for field in template["fields"]:
            for label in field.get("labels", [field["name"]]):
                all_labels.append(label)
                label_to_field[label] = field
        
        if not all_labels:
            return None
        
        match = process.extractOne(text, all_labels, scorer=fuzz.ratio)
        
        if match and match[1] >= threshold:
            matched_label = match[0]
            return {
                "field": label_to_field[matched_label],
                "matched_label": matched_label,
                "score": match[1]
            }
        return None
    
    def auto_detect_template(self, ocr_texts, threshold=60):
        """Auto-detect which template matches the document"""
        best_match = None
        best_score = 0
        
        combined_text = " ".join(ocr_texts[:20])
        
        for name, template in self.templates.items():
            score = 0
            for field in template["fields"]:
                for label in field.get("labels", []):
                    if fuzz.partial_ratio(label.lower(), combined_text.lower()) > 80:
                        score += 1
            
            if score > best_score:
                best_score = score
                best_match = name
        
        return best_match if best_score >= 3 else None