# field_config.py - Teaching the AI Your Form Structure
# ======================================================

INSURANCE_FORM_FIELDS = {
    "page_1": {
        "form_number": "F.N.:001",
        "fields": [
            {
                "id": "1.क",
                "name_en": "Full Name (Nepali)",
                "name_np": "नाम, थर",
                "type": "text",
                "patterns": ["नाम", "थर", "पुरा नाम"],
                "validation": "nepali_text"
            },
            {
                "id": "1.ख",
                "name_en": "Full Name (English)",
                "name_np": "NAME IN ENGLISH",
                "type": "text",
                "patterns": ["NAME IN ENGLISH", "BLOCK LETTER", "NAME"],
                "validation": "english_uppercase"
            },
            {
                "id": "1.ग.1",
                "name_en": "District",
                "name_np": "जिल्ला",
                "type": "text",
                "patterns": ["जिल्ला", "District"],
                "validation": "text"
            },
            {
                "id": "1.ग.2",
                "name_en": "Municipality",
                "name_np": "न.पा./गा.वि.स.",
                "type": "text",
                "patterns": ["न.पा.", "गा.वि.स.", "नगरपालिका", "Municipality"],
                "validation": "text"
            },
            {
                "id": "1.ग.3",
                "name_en": "Ward No",
                "name_np": "वडा नं.",
                "type": "number",
                "patterns": ["वडा", "Ward"],
                "validation": "number"
            },
            {
                "id": "1.ग.4",
                "name_en": "Phone",
                "name_np": "फोन नं.",
                "type": "phone",
                "patterns": ["फोन", "Phone", "Tel"],
                "validation": "phone"
            },
            {
                "id": "1.ग.5",
                "name_en": "Mobile",
                "name_np": "मोबाइल नं.",
                "type": "phone",
                "patterns": ["मोबाइल", "Mobile"],
                "validation": "mobile"
            },
            {
                "id": "1.ग.6",
                "name_en": "Email",
                "name_np": "इमेल",
                "type": "email",
                "patterns": ["इमेल", "Email", "E-mail"],
                "validation": "email"
            },
            {
                "id": "1.ङ",
                "name_en": "PAN Number",
                "name_np": "स्थायी लेखा नं.",
                "type": "text",
                "patterns": ["PAN", "स्थायी लेखा", "Permanent Account"],
                "validation": "pan"
            },
            {
                "id": "1.च",
                "name_en": "Date of Birth",
                "name_np": "जन्म मिति",
                "type": "date",
                "patterns": ["जन्म मिति", "Date of Birth", "DOB"],
                "validation": "date_bs"
            },
            {
                "id": "1.छ",
                "name_en": "Nationality",
                "name_np": "राष्ट्रियता",
                "type": "text",
                "patterns": ["राष्ट्रियता", "Nationality"],
                "validation": "text"
            },
            {
                "id": "1.ज",
                "name_en": "Occupation",
                "name_np": "पेशा",
                "type": "text",
                "patterns": ["पेशा", "Occupation", "व्यवसाय"],
                "validation": "text"
            },
            {
                "id": "1.भ",
                "name_en": "Monthly Income",
                "name_np": "मासिक आय",
                "type": "currency",
                "patterns": ["मासिक आय", "Monthly Income", "आम्दानी"],
                "validation": "currency"
            }
        ]
    },
    "page_2": {
        "form_number": "F.N.:001",
        "fields": [
            {
                "id": "2.क",
                "name_en": "Insurance Plan",
                "name_np": "बीमा योजना",
                "type": "text",
                "patterns": ["बीमा योजना", "Plan", "Insurance Plan"],
                "validation": "text"
            },
            {
                "id": "2.ख",
                "name_en": "Policy Term",
                "name_np": "बीमा अवधि",
                "type": "number",
                "patterns": ["अवधि", "Term", "वर्ष"],
                "validation": "number"
            },
            {
                "id": "2.ग",
                "name_en": "Sum Assured",
                "name_np": "बीमाङ्क",
                "type": "currency",
                "patterns": ["बीमाङ्क", "Sum Assured", "बीमा रकम"],
                "validation": "currency"
            },
            {
                "id": "3.क",
                "name_en": "Nominee Name",
                "name_np": "इच्छाएको व्यक्ति",
                "type": "text",
                "patterns": ["इच्छाएको", "Nominee", "हकवाला"],
                "validation": "text"
            },
            {
                "id": "3.ङ",
                "name_en": "Relationship",
                "name_np": "सम्बन्ध",
                "type": "text",
                "patterns": ["सम्बन्ध", "Relationship", "नाता"],
                "validation": "text"
            }
        ]
    }
}

# Validation patterns
VALIDATION_RULES = {
    "nepali_text": r'[\u0900-\u097F\s]+',
    "english_uppercase": r'[A-Z\s]+',
    "text": r'.+',
    "number": r'\d+',
    "phone": r'\d{2}-\d{7,8}',
    "mobile": r'9\d{9}',
    "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    "pan": r'\d{9}',
    "date_bs": r'\d{4}/\d{2}/\d{2}',
    "currency": r'[\d,]+'
}
