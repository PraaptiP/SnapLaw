"""
Utility functions for SnapLaw
"""

import subprocess
import sys
import re
import logging
try:
    import PyPDF2
    from PIL import Image
except ImportError as e:
    print(f"Warning: {e}")
    PyPDF2 = None
    Image = None

# Configure logging
logger = logging.getLogger(__name__)

# Risk patterns for detection
RISK_PATTERNS = {
    "binding_arbitration": {
        "patterns": [
            r"binding arbitration", r"arbitration clause", r"waive.*right.*jury trial",
            r"resolve.*disputes.*arbitration", r"mandatory arbitration"
        ],
        "type": "Binding Arbitration",
        "severity": "High",
        "explanation": "You may be giving up your right to sue in court and must resolve disputes through arbitration."
    },
    "non_refundable": {
        "patterns": [
            r"non-refundable", r"no refunds?", r"all sales final",
            r"payments?.*not.*refund", r"fees are final"
        ],
        "type": "Non-refundable",
        "severity": "Medium",
        "explanation": "You may not be able to get your money back under any circumstances."
    },
    "automatic_renewal": {
        "patterns": [
            r"automatic.*renewal", r"auto.*renew", r"automatically.*extend",
            r"renew.*unless.*cancel", r"auto-renewal"
        ],
        "type": "Auto-renewal",
        "severity": "Medium",
        "explanation": "The contract will automatically renew unless you actively cancel it."
    },
    "liability_waiver": {
        "patterns": [
            r"waive.*liability", r"not.*liable.*damages", r"disclaim.*warranties",
            r"use.*at.*own.*risk", r"hold harmless"
        ],
        "type": "Liability Waiver",
        "severity": "High",
        "explanation": "The company may not be responsible for damages or problems that occur."
    },
    "data_collection": {
        "patterns": [
            r"collect.*personal.*data", r"share.*information.*third.*parties",
            r"sell.*data", r"tracking.*cookies", r"personal information"
        ],
        "type": "Data Collection",
        "severity": "Medium",
        "explanation": "Your personal information may be collected, stored, or shared with other companies."
    },
    "termination_rights": {
        "patterns": [
            r"terminate.*at.*will", r"suspend.*account.*any.*time",
            r"discontinue.*service.*notice", r"modify.*terms.*without.*notice"
        ],
        "type": "Unfair Termination",
        "severity": "High",
        "explanation": "The company can end the agreement or change terms with little or no notice."
    }
}

def install_packages():
    """Install required packages"""
    packages = [
        'flask',
        'google-generativeai',
        'Pillow',
        'PyPDF2',
        'werkzeug',
        'pyngrok==7.0.0',  # Fixed version for compatibility
        'nest-asyncio'  # Required for Colab
    ]

    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    if not PyPDF2:
        raise Exception("PyPDF2 not available")
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise Exception(f"Could not extract text from PDF: {str(e)}")

def extract_text_from_image(file_path, model):
    """Extract text from image using Gemini Vision"""
    try:
        image = Image.open(file_path)
        prompt = "Extract all text from this image. If this appears to be a legal document or contract, preserve the formatting and structure. Return only the extracted text."
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        logger.error(f"Image OCR error: {e}")
        raise Exception(f"Could not extract text from image: {str(e)}")

def detect_risk_clauses(text):
    """Detect risky clauses in the document"""
    risks = []
    text_lower = text.lower()

    for risk_key, risk_info in RISK_PATTERNS.items():
        for pattern in risk_info["patterns"]:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                # Find the sentence containing the match
                start = max(0, text.rfind('.', 0, match.start()) + 1)
                end = text.find('.', match.end())
                if end == -1:
                    end = len(text)

                sentence = text[start:end].strip()
                if len(sentence) > 20:  # Only include meaningful sentences
                    risks.append({
                        "text": sentence,
                        "type": risk_info["type"],
                        "severity": risk_info["severity"],
                        "explanation": risk_info["explanation"]
                    })
                    break  # Only one match per pattern per risk type

    return risks

def calculate_complexity_score(text):
    """Calculate document complexity score (1-10)"""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return 1.0

    avg_words_per_sentence = len(words) / len(sentences)

    # Legal jargon detection
    legal_terms = [
        'whereas', 'heretofore', 'hereinafter', 'notwithstanding', 'aforementioned',
        'pursuant', 'thereof', 'hereby', 'hereunder', 'indemnify', 'covenant',
        'warranty', 'liability', 'jurisdiction', 'arbitration', 'severability',
        'consideration', 'breach', 'termination', 'governing', 'enforceable'
    ]

    legal_term_count = sum(1 for word in words if word.lower() in legal_terms)
    legal_density = (legal_term_count / len(words)) * 100 if words else 0

    # Calculate complexity
    sentence_complexity = min(avg_words_per_sentence / 15, 2.0)
    term_complexity = min(legal_density / 2, 2.0)

    return min((sentence_complexity + term_complexity) * 2.5, 10.0)

def calculate_risk_score(risk_clauses, complexity, word_count):
    """Calculate overall risk score (1-10)"""
    clause_risk = 0
    for clause in risk_clauses:
        if clause["severity"] == "High":
            clause_risk += 3
        elif clause["severity"] == "Medium":
            clause_risk += 2
        else:
            clause_risk += 1

    length_factor = min(word_count / 1000, 2.0)
    complexity_factor = complexity / 10

    return min((clause_risk * 0.6) + (length_factor * 0.2) + (complexity_factor * 0.2), 10.0)