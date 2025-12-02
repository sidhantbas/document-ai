# exporter.py - Export to Excel/CSV

import json
import io

class Exporter:
    
    @staticmethod
    def to_excel(extracted_data, filename="export.xlsx"):
        """Export to Excel"""
        import pandas as pd
        
        rows = []
        for field_name, data in extracted_data.items():
            rows.append({
                "Field": field_name,
                "Value": data.get("value", ""),
                "Raw": data.get("raw", ""),
                "Type": data.get("type", ""),
                "Confidence": data.get("confidence", 0)
            })
        
        df = pd.DataFrame(rows)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Extracted Data')
        
        return buffer.getvalue()
    
    @staticmethod
    def to_csv(extracted_data):
        """Export to CSV"""
        import pandas as pd
        
        rows = []
        for field_name, data in extracted_data.items():
            rows.append({
                "Field": field_name,
                "Value": data.get("value", ""),
                "Confidence": data.get("confidence", 0)
            })
        
        df = pd.DataFrame(rows)
        return df.to_csv(index=False)
    
    @staticmethod
    def to_json(extracted_data):
        """Export to JSON"""
        return json.dumps(extracted_data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def batch_to_excel(all_extractions):
        """Export multiple documents to single Excel"""
        import pandas as pd
        
        all_rows = []
        for doc_name, extracted in all_extractions.items():
            for field_name, data in extracted.items():
                all_rows.append({
                    "Document": doc_name,
                    "Field": field_name,
                    "Value": data.get("value", ""),
                    "Confidence": data.get("confidence", 0)
                })
        
        df = pd.DataFrame(all_rows)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='All Documents')
        
        return buffer.getvalue()