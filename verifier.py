# verifier.py - Cross-Document Verification

class Verifier:
    
    @staticmethod
    def verify_name_match(name1, name2, threshold=85):
        """Check if two names match"""
        from rapidfuzz import fuzz
        score = fuzz.ratio(name1.upper(), name2.upper())
        return {
            "match": score >= threshold,
            "score": score,
            "field": "Name"
        }
    
    @staticmethod
    def verify_date(date_str):
        """Validate BS date"""
        import re
        if not date_str:
            return {"valid": False, "error": "Empty date"}
        
        match = re.match(r'(\d{4})/(\d{2})/(\d{2})', date_str)
        if not match:
            return {"valid": False, "error": "Invalid format"}
        
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        
        if not (1970 <= year <= 2090):
            return {"valid": False, "error": "Year out of range"}
        if not (1 <= month <= 12):
            return {"valid": False, "error": "Invalid month"}
        if not (1 <= day <= 32):
            return {"valid": False, "error": "Invalid day"}
        
        return {"valid": True, "parsed": {"year": year, "month": month, "day": day}}
    
    @staticmethod
    def verify_phone(phone):
        """Validate Nepali phone"""
        import re
        if not phone:
            return {"valid": False, "error": "Empty"}
        
        phone = re.sub(r'\D', '', phone)
        
        if len(phone) == 10 and phone.startswith('9'):
            return {"valid": True, "type": "Mobile"}
        elif len(phone) >= 7:
            return {"valid": True, "type": "Landline"}
        
        return {"valid": False, "error": "Invalid format"}
    
    @staticmethod
    def verify_email(email):
        """Validate email"""
        import re
        if not email:
            return {"valid": False, "error": "Empty"}
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return {"valid": True}
        return {"valid": False, "error": "Invalid format"}
    
    @staticmethod
    def verify_pan(pan):
        """Validate PAN"""
        import re
        if not pan:
            return {"valid": False, "error": "Empty"}
        
        if re.match(r'^\d{9}$', pan):
            return {"valid": True}
        return {"valid": False, "error": "Must be 9 digits"}
    
    @staticmethod
    def run_all_checks(extracted_data):
        """Run all verification checks"""
        results = {"passed": 0, "failed": 0, "checks": []}
        
        # Date of Birth
        dob = extracted_data.get("Date of Birth", {}).get("value", "")
        dob_check = Verifier.verify_date(dob)
        dob_check["field"] = "Date of Birth"
        results["checks"].append(dob_check)
        if dob_check.get("valid"):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Phone
        phone = extracted_data.get("Phone", {}).get("value", "") or extracted_data.get("Mobile", {}).get("value", "")
        phone_check = Verifier.verify_phone(phone)
        phone_check["field"] = "Phone"
        results["checks"].append(phone_check)
        if phone_check.get("valid"):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Email
        email = extracted_data.get("Email", {}).get("value", "")
        email_check = Verifier.verify_email(email)
        email_check["field"] = "Email"
        results["checks"].append(email_check)
        if email_check.get("valid"):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # PAN
        pan = extracted_data.get("PAN", {}).get("value", "")
        pan_check = Verifier.verify_pan(pan)
        pan_check["field"] = "PAN"
        results["checks"].append(pan_check)
        if pan_check.get("valid"):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        results["total"] = results["passed"] + results["failed"]
        results["score"] = f"{results['passed']}/{results['total']}"
        
        return results