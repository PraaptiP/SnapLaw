#!/usr/bin/env python3
"""
Unit tests for SnapLaw - AI-Powered Legal Document Analyzer
"""

import unittest
import os
import tempfile
import sys
from io import StringIO
from unittest.mock import Mock, patch, MagicMock
import json

# Add the parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies before importing
sys.modules['google.generativeai'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PyPDF2'] = MagicMock()
sys.modules['nest_asyncio'] = MagicMock()
sys.modules['pyngrok'] = MagicMock()

# Import after mocking
from paste import DocumentAnalyzer, app, RISK_PATTERNS


class TestDocumentAnalyzer(unittest.TestCase):
    """Test cases for DocumentAnalyzer class"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = DocumentAnalyzer()
        self.sample_text = """
        This agreement contains binding arbitration clauses.
        All payments are non-refundable under any circumstances.
        We may terminate this agreement at any time without notice.
        Your data will be shared with third parties for marketing purposes.
        """

    def test_detect_risk_clauses(self):
        """Test risk clause detection"""
        risks = self.analyzer.detect_risk_clauses(self.sample_text)
        
        # Should detect multiple risk types
        self.assertGreater(len(risks), 0)
        
        # Check for specific risk types
        risk_types = [risk['type'] for risk in risks]
        self.assertIn('Binding Arbitration', risk_types)
        self.assertIn('Non-refundable', risk_types)

    def test_calculate_complexity_score(self):
        """Test complexity score calculation"""
        simple_text = "This is a simple contract. It has short sentences."
        complex_text = """
        Notwithstanding the aforementioned provisions hereinafter described,
        the party of the first part hereby covenants and agrees to indemnify
        and hold harmless the party of the second part from any and all
        liability, damages, or claims pursuant to this agreement.
        """
        
        simple_score = self.analyzer.calculate_complexity_score(simple_text)
        complex_score = self.analyzer.calculate_complexity_score(complex_text)
        
        self.assertGreater(complex_score, simple_score)
        self.assertGreaterEqual(simple_score, 1.0)
        self.assertLessEqual(complex_score, 10.0)

    def test_calculate_risk_score(self):
        """Test risk score calculation"""
        high_risk_clauses = [
            {'severity': 'High'}, {'severity': 'High'}, {'severity': 'Medium'}
        ]
        low_risk_clauses = [
            {'severity': 'Low'}, {'severity': 'Low'}
        ]
        
        high_score = self.analyzer.calculate_risk_score(high_risk_clauses, 8.0, 2000)
        low_score = self.analyzer.calculate_risk_score(low_risk_clauses, 3.0, 500)
        
        self.assertGreater(high_score, low_score)
        self.assertGreaterEqual(low_score, 1.0)
        self.assertLessEqual(high_score, 10.0)

    def test_risk_patterns_coverage(self):
        """Test that all risk patterns are properly configured"""
        for risk_key, risk_info in RISK_PATTERNS.items():
            self.assertIn('patterns', risk_info)
            self.assertIn('type', risk_info)
            self.assertIn('severity', risk_info)
            self.assertIn('explanation', risk_info)
            
            self.assertIsInstance(risk_info['patterns'], list)
            self.assertGreater(len(risk_info['patterns']), 0)
            self.assertIn(risk_info['severity'], ['Low', 'Medium', 'High'])

    @patch('google.generativeai.GenerativeModel')
    def test_generate_summary_with_mock(self, mock_model_class):
        """Test summary generation with mocked Gemini"""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "This is a test summary of the legal document."
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Create analyzer with mocked model
        analyzer = DocumentAnalyzer()
        analyzer.model = mock_model
        
        summary = analyzer.generate_summary(self.sample_text)
        
        self.assertEqual(summary, "This is a test summary of the legal document.")
        mock_model.generate_content.assert_called_once()

    def test_extract_key_terms_fallback(self):
        """Test key terms extraction fallback when API fails"""
        # Set model to None to simulate API failure
        self.analyzer.model = None
        
        terms = self.analyzer.extract_key_terms(self.sample_text)
        
        self.assertIsInstance(terms, list)
        self.assertIn("Key terms unavailable", terms[0])

    def test_answer_question_fallback(self):
        """Test question answering fallback when API fails"""
        # Set model to None to simulate API failure
        self.analyzer.model = None
        
        answer = self.analyzer.answer_question("What is this about?", self.sample_text)
        
        self.assertIn("unavailable", answer)


class TestFlaskApp(unittest.TestCase):
    """Test cases for Flask application"""

    def setUp(self):
        """Set up test client"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_index_route(self):
        """Test main index route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SnapLaw', response.data)

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')

    def test_analyze_no_file(self):
        """Test analyze endpoint without file"""
        response = self.client.post('/analyze')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('No file uploaded', data['error'])

    def test_ask_no_question(self):
        """Test ask endpoint without question"""
        response = self.client.post('/ask', 
                                   data=json.dumps({}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_file_too_large_error(self):
        """Test file too large error handling"""
        # Create a mock large file
        large_content = b'x' * (17 * 1024 * 1024)  # 17MB
        
        with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
            temp_file.write(large_content)
            temp_file.seek(0)
            
            response = self.client.post('/analyze', 
                                       data={'file': (temp_file, 'large.txt')})
            
            # Should return 413 (Payload Too Large) or handle gracefully
            self.assertIn(response.status_code, [200, 413])


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""

    def test_install_packages_function(self):
        """Test package installation function exists and is callable"""
        from paste import install_packages
        
        # Should be callable (we won't actually run it in tests)
        self.assertTrue(callable(install_packages))

    def test_main_function_exists(self):
        """Test main function exists"""
        from paste import main
        
        self.assertTrue(callable(main))

    def test_ngrok_functions_exist(self):
        """Test ngrok-related functions exist"""
        from paste import setup_ngrok, run_with_ngrok, run_local
        
        self.assertTrue(callable(setup_ngrok))
        self.assertTrue(callable(run_with_ngrok))
        self.assertTrue(callable(run_local))


class TestConfigurationValidation(unittest.TestCase):
    """Test configuration and constants"""

    def test_risk_patterns_structure(self):
        """Test RISK_PATTERNS dictionary structure"""
        required_keys = ['patterns', 'type', 'severity', 'explanation']
        
        for pattern_key, pattern_data in RISK_PATTERNS.items():
            for key in required_keys:
                self.assertIn(key, pattern_data, 
                            f"Missing key '{key}' in pattern '{pattern_key}'")

    def test_flask_config(self):
        """Test Flask app configuration"""
        self.assertIsNotNone(app.config.get('MAX_CONTENT_LENGTH'))
        self.assertEqual(app.config['MAX_CONTENT_LENGTH'], 16 * 1024 * 1024)

    def test_allowed_extensions(self):
        """Test that common file extensions would be handled"""
        # This tests the logic that would be used in file validation
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.txt'}
        
        test_files = [
            'test.pdf', 'test.jpg', 'test.jpeg', 'test.png', 'test.txt'
        ]
        
        for filename in test_files:
            ext = os.path.splitext(filename.lower())[1]
            self.assertIn(ext, allowed_extensions, 
                         f"Extension {ext} should be allowed")


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestDocumentAnalyzer,
        TestFlaskApp,
        TestUtilityFunctions,
        TestConfigurationValidation
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)