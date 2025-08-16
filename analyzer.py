"""
DocumentAnalyzer - AI-powered legal document analysis
"""

import os
import re
import logging
import google.generativeai as genai
from PIL import Image
from utils import extract_text_from_pdf, extract_text_from_image, detect_risk_clauses, calculate_complexity_score, calculate_risk_score

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBFWnRCGi74-bPV1U6a-D6zBLIf8rMYfMU")
genai.configure(api_key=GEMINI_API_KEY)

class DocumentAnalyzer:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.current_document_text = None
            print("✅ Gemini model initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Gemini model: {e}")
            self.model = None

    def generate_summary(self, text):
        """Generate document summary using Gemini"""
        if not self.model:
            return "Summary unavailable - Gemini model not initialized"

        prompt = f"""Create a brief, clear summary of this legal document in plain English.
        Focus on the key points, obligations, and important terms. Maximum 200 words.

        Document:
        {text[:3000]}

        Summary:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return "Summary could not be generated due to an error."

    def simplify_text(self, text):
        """Simplify legal text to plain English"""
        if not self.model:
            return "Simplified text unavailable - Gemini model not initialized"

        prompt = f"""Please simplify the following legal text into plain English that anyone can understand.
        Keep the meaning intact but make it accessible to non-lawyers. Use simple words, shorter sentences,
        and everyday language.

        Legal Text:
        {text[:3000]}

        Simplified Version:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Text simplification error: {e}")
            return "Text could not be simplified due to an error."

    def extract_key_terms(self, text):
        """Extract key legal terms"""
        if not self.model:
            return ["Key terms unavailable - Gemini model not initialized"]

        prompt = f"""Extract the most important legal terms and concepts from this document.
        Return only a comma-separated list of terms, maximum 15 terms. Focus on key obligations,
        rights, penalties, and important concepts.

        Document:
        {text[:2000]}

        Key terms:"""

        try:
            response = self.model.generate_content(prompt)
            terms = [term.strip() for term in response.text.split(',')]
            return terms[:15]
        except Exception as e:
            logger.error(f"Key terms extraction error: {e}")
            return ["Terms could not be extracted"]

    def answer_question(self, question, document_text):
        """Answer questions about the document"""
        if not self.model:
            return "Question answering unavailable - Gemini model not initialized"

        prompt = f"""Based on the following legal document, please answer this question accurately and concisely:

        Question: {question}

        Document:
        {document_text[:4000]}

        Answer:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Question answering error: {e}")
            return "I couldn't answer that question due to an error."

    def analyze_document(self, file_path, filename):
        """Main analysis function"""
        try:
            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                text = extract_text_from_image(file_path, self.model)
            else:  # Text file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()

            if not text or len(text.strip()) < 50:
                raise Exception("Document appears to be empty or too short to analyze")

            self.current_document_text = text

            # Perform analysis
            word_count = len(text.split())
            complexity_score = calculate_complexity_score(text)
            risk_clauses = detect_risk_clauses(text)
            risk_score = calculate_risk_score(risk_clauses, complexity_score, word_count)

            # Generate AI content
            summary = self.generate_summary(text)
            simplified_text = self.simplify_text(text)
            key_terms = self.extract_key_terms(text)

            return {
                "word_count": word_count,
                "complexity_score": complexity_score,
                "risk_clauses": risk_clauses,
                "risk_score": risk_score,
                "summary": summary,
                "simplified_text": simplified_text,
                "key_terms": key_terms,
                "original_text": text[:1000] + "..." if len(text) > 1000 else text
            }

        except Exception as e:
            logger.error(f"Document analysis error: {e}")
            raise Exception(f"Analysis failed: {str(e)}")