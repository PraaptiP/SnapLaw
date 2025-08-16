#!/usr/bin/env python3
"""
SnapLaw - AI-Powered Legal Document Analyzer
Main Flask Application
"""

import os
import tempfile
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from analyzer import DocumentAnalyzer
from utils import install_packages
import nest_asyncio
from pyngrok import ngrok, conf
from pathlib import Path
try:
    from flask_cors import CORS
except ImportError:
    print("Warning: flask-cors not installed, CORS might not work properly")
    CORS = None

# Import the function to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed")

# Apply nest_asyncio for Colab compatibility
nest_asyncio.apply()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
if CORS:
    CORS(app)

# Create the upload folder if it doesn't exist
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'snaplaw_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Get API keys and tokens from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "").strip()

# Initialize analyzer
analyzer = DocumentAnalyzer()

@app.route('/')
def index():
    """Serve the main HTML interface"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_document():
    """Handle document upload and analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"})

        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"})

        # Validate file type
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.txt'}
        file_ext = os.path.splitext(file.filename.lower())[1]
        if file_ext not in allowed_extensions:
            return jsonify({"success": False, "error": "Unsupported file type"})

        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            # Analyze the document
            analysis = analyzer.analyze_document(file_path, filename)

            # Clean up uploaded file
            os.remove(file_path)

            return jsonify({
                "success": True,
                "analysis": analysis
            })

        except Exception as analysis_error:
            # Clean up uploaded file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise analysis_error

    except Exception as e:
        logger.error(f"Analysis endpoint error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle question answering"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()

        if not question:
            return jsonify({"success": False, "error": "No question provided"})

        if not analyzer.current_document_text:
            return jsonify({"success": False, "error": "No document analyzed yet"})

        answer = analyzer.answer_question(question, analyzer.current_document_text)

        return jsonify({
            "success": True,
            "answer": answer
        })

    except Exception as e:
        logger.error(f"Question answering error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_configured": bool(GEMINI_API_KEY and analyzer.model),
        "upload_folder": app.config['UPLOAD_FOLDER']
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({"success": False, "error": "File too large. Maximum size is 16MB."}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500

def setup_ngrok():
    """Setup ngrok with authentication"""
    try:
        # Kill any existing ngrok processes
        try:
            ngrok.kill()
        except Exception:
            pass  # Ignore if no processes to kill

        # Check token
        if not NGROK_AUTH_TOKEN or "YOUR_TOKEN" in NGROK_AUTH_TOKEN:
            print("❌ Ngrok token not configured properly")
            return False

        # Set the auth token
        try:
            ngrok.set_auth_token(NGROK_AUTH_TOKEN)
            print("✅ Ngrok authentication configured")
            return True
        except PermissionError:
            print("❌ Permission denied: Try running as administrator")
            return False
        except Exception as e:
            print(f"❌ Ngrok authentication error: {e}")
            return False

    except Exception as e:
        print(f"❌ Ngrok setup error: {e}")
        return False

def run_with_ngrok():
    """Run Flask app with ngrok tunnel"""
    try:
        # Setup ngrok
        if not setup_ngrok():
            raise Exception("Failed to setup ngrok")

        # Create tunnel
        public_url = ngrok.connect(5000, bind_tls=True)
        print(f"\n🌐 Public URL: {public_url}")
        print(f"🔗 Access your SnapLaw app at: {public_url}")
        print("📱 Share this URL to access from any device!")
        print("=" * 60)

        # Run Flask app
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)

    except Exception as e:
        print(f"❌ Error running with ngrok: {e}")
        print("🔄 Trying local hosting as fallback...")
        run_local()

def run_local():
    """Run Flask app locally without ngrok"""
    try:
        print("🏠 Running locally at: http://127.0.0.1:5000")
        print("📝 Note: Only accessible from this machine")
        print("=" * 50)
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Local hosting error: {e}")

def main():
    """Main function to run the application"""
    print("🚀 Starting SnapLaw - AI Legal Document Analyzer")
    print("📍 Optimized for Local Development")
    print("=" * 60)

    # Install packages first
    print("📦 Installing required packages...")
    install_packages()

    # Check API configuration
    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "" or "YOUR_API_KEY" in GEMINI_API_KEY:
        print("❌ ERROR: Please set your Gemini API key!")
        print("🔑 Add GEMINI_API_KEY to your .env file")
        print("🔗 Get your API key from: https://makersuite.google.com/app/apikey")
        return

    print(f"✅ Gemini API configured")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")

    # Test Gemini connection
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        test_model = genai.GenerativeModel('gemini-1.5-flash')
        test_response = test_model.generate_content("Test connection")
        print("✅ Gemini API connection successful")
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        print("🔧 Please check your API key and internet connection")
        return

    # Test ngrok token
    if not NGROK_AUTH_TOKEN or "YOUR_TOKEN" in NGROK_AUTH_TOKEN:
        print("⚠️  Warning: Ngrok token not configured, running locally...")
        run_local()
    else:
        print("🌐 Setting up public access with ngrok...")
        run_with_ngrok()

# Auto-run functions for easy usage
def start_snaplaw():
    """Simple function to start SnapLaw"""
    main()

def start_local():
    """Start SnapLaw locally without ngrok"""
    print("🏠 Starting SnapLaw locally...")
    run_local()

def start_public():
    """Start SnapLaw with public ngrok access"""
    print("🌐 Starting SnapLaw with public access...")
    run_with_ngrok()

if __name__ == "__main__":
    main()