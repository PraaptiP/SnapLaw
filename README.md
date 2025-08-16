# SnapLaw 📄⚖️

**AI-Powered Legal Document Analyzer** - Transform complex legal documents into clear, understandable insights.

SnapLaw uses Google's Gemini AI to analyze contracts, terms of service, and legal documents, identifying risk clauses and providing plain-English explanations to help you make informed decisions.

## ✨ Features

- **📊 Comprehensive Analysis**: Risk scoring and complexity assessment
- **⚠️ Intelligent Risk Detection**: Identifies dangerous clauses like binding arbitration, liability waivers, and auto-renewal terms
- **📖 Plain English Translation**: Converts legal jargon into simple, understandable language
- **🔑 Key Terms Extraction**: Highlights important legal concepts and obligations
- **❓ Interactive Q&A**: Ask specific questions about your document
- **📱 Multi-format Support**: PDF, images (JPG/PNG), and text files
- **🔒 Privacy-focused**: Documents processed temporarily, no permanent storage

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/snaplaw.git
   cd snaplaw
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```
   
   Open your browser and navigate to `http://localhost:5000`

## 📖 Usage

1. **Upload Document**: Drag and drop or click to upload your legal document (PDF, image, or text file)
2. **View Analysis**: Get instant comprehensive analysis with risk assessment
3. **Explore Results**: 
   - **Summary**: Quick overview of the document
   - **Risk Analysis**: Identified problematic clauses with explanations
   - **Plain English**: Simplified version of complex legal terms
   - **Key Terms**: Important legal concepts extracted
4. **Ask Questions**: Use the interactive Q&A to get specific information about your document

## 🔍 Risk Detection Capabilities

SnapLaw automatically identifies common problematic clauses:

| Risk Level | Clause Types | Examples |
|------------|-------------|----------|
| **High Risk** | Binding Arbitration, Liability Waivers, Unfair Termination | Waiving jury trial rights, one-sided termination clauses |
| **Medium Risk** | Auto-renewal, Data Collection, Non-refundable Terms | Automatic contract extensions, broad data usage rights |
| **Low Risk** | Standard Terms, Common Provisions | Typical business terms, standard legal language |

## 📁 Project Structure

```
SnapLaw/
├── app.py                 # Flask application and routes
├── analyzer.py            # AI document analysis logic
├── utils.py              # Helper functions (PDF, OCR, risk detection)
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── templates/
│   └── index.html        # Web interface
└── tests/
    └── test_analyzer.py  # Unit tests
```

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `FLASK_ENV` | Flask environment | No | `production` |
| `MAX_CONTENT_LENGTH` | Max upload size (bytes) | No | `16MB` |

### Supported File Formats

- **PDF**: Text extraction using PyPDF2
- **Images**: JPG, JPEG, PNG (OCR via Gemini Vision)
- **Text**: Direct text file processing

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. tests/
```

## 🔒 Security & Privacy

- ✅ Documents processed in real-time, no permanent storage
- ✅ API keys secured via environment variables  
- ✅ No user data retention or tracking
- ✅ Temporary file cleanup after processing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## 📋 Roadmap

- [ ] Support for DOCX and RTF formats
- [ ] Batch document processing
- [ ] Document comparison features
- [ ] Custom risk pattern definitions
- [ ] Multi-language support
- [ ] REST API endpoints
- [ ] Document revision tracking

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) for powerful document analysis
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [PyPDF2](https://pypdf2.readthedocs.io/) for PDF processing
- All contributors who help make legal documents more accessible

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/snaplaw/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/snaplaw/discussions)
- 📧 **Contact**: [your-email@example.com]

---

<div align="center">

**Made with ❤️ for legal transparency and accessibility**

[⭐ Star this repo](https://github.com/yourusername/snaplaw) if you find it useful!

</div>