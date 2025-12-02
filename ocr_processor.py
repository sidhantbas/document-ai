# ocr_processor.py - Smart OCR with Post-Processing
# ==================================================

import re
from rapidfuzz import fuzz

class OCRProcessor:
    
    # Common OCR errors and fixes
    OCR_FIXES = {
        '0': 'O',  # Zero to O
        '1': 'I',  # One to I
        '|': 'I',  # Pipe to I
        'l': '1',  # lowercase L to 1 (in numbers)
        'रु': 'रु.',
        'Rs': 'Rs.',
    }
    
    # Nepali digit mapping
    NEPALI_DIGITS = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    
    @staticmethod
    def normalize_nepali_numbers(text):
        """Convert Nepali digits to English"""
        for nep, eng in OCRProcessor.NEPALI_DIGITS.items():
            text = text.replace(nep, eng)
        return text
    
    @staticmethod
    def clean_text(text):
        """Basic text cleaning"""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    
    @staticmethod
    def extract_phone(text):
        """Extract phone number"""
        text = OCRProcessor.normalize_nepali_numbers(text)
        patterns = [
            r'9[78]\d{8}',           # Mobile: 98XXXXXXXX
            r'\d{2,3}-\d{6,8}',      # Landline: 01-XXXXXXX
            r'\d{10}',               # 10 digits
        ]
        for p in patterns:
            match = re.search(p, text)
            if match:
                return match.group()
        return None
    
    @staticmethod
    def extract_email(text):
        """Extract email"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group() if match else None
    
    @staticmethod
    def extract_date_bs(text):
        """Extract Nepali date (BS)"""
        text = OCRProcessor.normalize_nepali_numbers(text)
        patterns = [
            r'20[0-9]{2}/[01][0-9]/[0-3][0-9]',  # 2045/03/15
            r'20[0-9]{2}-[01][0-9]-[0-3][0-9]',  # 2045-03-15
            r'20[0-9]{2}\.[01][0-9]\.[0-3][0-9]', # 2045.03.15
        ]
        for p in patterns:
            match = re.search(p, text)
            if match:
                return match.group().replace('-', '/').replace('.', '/')
        return None
    
    @staticmethod
    def extract_currency(text):
        """Extract currency amount"""
        text = OCRProcessor.normalize_nepali_numbers(text)
        text = text.replace(',', '')
        pattern = r'(?:Rs\.?|NPR|रु\.?)\s*([\d,]+(?:\.\d{2})?)'
        match = re.search(pattern, text)
        if match:
            return f"Rs. {match.group(1)}"
        
        # Just numbers with commas
        pattern2 = r'([\d,]{4,})'
        match2 = re.search(pattern2, text)
        if match2:
            return match2.group(1)
        return None
    
    @staticmethod
    def extract_pan(text):
        """Extract PAN number"""
        text = OCRProcessor.normalize_nepali_numbers(text)
        pattern = r'\d{9}'
        match = re.search(pattern, text)
        return match.group() if match else None
    
    @staticmethod
    def validate_and_extract(text, field_type):
        """Validate and extract based on field type"""
        extractors = {
            "phone": OCRProcessor.extract_phone,
            "mobile": OCRProcessor.extract_phone,
            "email": OCRProcessor.extract_email,
            "date": OCRProcessor.extract_date_bs,
            "date_bs": OCRProcessor.extract_date_bs,
            "currency": OCRProcessor.extract_currency,
            "amount": OCRProcessor.extract_currency,
            "pan": OCRProcessor.extract_pan,
        }
        
        extractor = extractors.get(field_type)
        if extractor:
            return extractor(text)
        return OCRProcessor.clean_text(text)
    
    @staticmethod
    def find_value_near_label(ocr_results, label_index, direction="right"):
        """Find value near a label"""
        if label_index >= len(ocr_results) - 1:
            return None
        
        label_item = ocr_results[label_index]
        label_bbox = label_item.get("bbox", [[0,0]])
        label_y = label_bbox[0][1] if label_bbox else 0
        
        candidates = []
        
        for i, item in enumerate(ocr_results):
            if i == label_index:
                continue
            
            item_bbox = item.get("bbox", [[0,0]])
            item_y = item_bbox[0][1] if item_bbox else 0
            
            # Same line (within 20 pixels)
            if abs(item_y - label_y) < 20:
                if direction == "right" and i > label_index:
                    candidates.append(item)
            
            # Next line
            elif item_y > label_y and item_y - label_y < 50:
                candidates.append(item)
        
        if candidates:
            return candidates[0]["text"]
        return None
    
    @staticmethod
    def process_results(ocr_results, template_fields):
        """Process OCR results with smart extraction"""
        from rapidfuzz import fuzz, process
        
        extracted = {}
        texts = [r["text"] for r in ocr_results]
        
        for field in template_fields:
            field_name = field["name"]
            field_type = field.get("type", "text")
            labels = field.get("labels", [field_name])
            
            # Find matching label
            for i, text in enumerate(texts):
                for label in labels:
                    if fuzz.partial_ratio(label.lower(), text.lower()) > 75:
                        # Found label, look for value
                        value = OCRProcessor.find_value_near_label(ocr_results, i)
                        
                        if value:
                            clean_value = OCRProcessor.validate_and_extract(value, field_type)
                            if clean_value:
                                extracted[field_name] = {
                                    "value": clean_value,
                                    "raw": value,
                                    "type": field_type,
                                    "confidence": ocr_results[i].get("confidence", 0)
                                }
                        break
        
        return extracted