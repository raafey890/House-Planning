import unittest
from unittest.mock import patch, MagicMock
from app.services.ai.gemini_provider import GeminiProvider

class TestGeminiProviderRetries(unittest.TestCase):
    def setUp(self):
        self.provider = GeminiProvider(model_name="test-model")
        
    @patch('app.services.ai.prompt_builder.build_prompt', return_value="prompt")
    @patch('google.genai.Client')
    def test_first_503_second_succeeds(self, mock_client_cls, mock_build):
        mock_client = MagicMock()
        self.provider.client = mock_client
        
        mock_response = MagicMock()
        mock_response.text = '{"schema_version": "1.0", "units": "ft", "plot": {"width": 10, "length": 10, "facing": "North", "buildable_boundary": {"width": 8, "length": 8}, "setbacks": {}}}'
        
        # First call raises 503, second returns success
        mock_client.models.generate_content.side_effect = [
            Exception("503 UNAVAILABLE: The model is overloaded"),
            mock_response
        ]
        
        # Patch sleep to avoid waiting
        with patch('time.sleep') as mock_sleep:
            result = self.provider.generate_layout({})
            
            # Should have called sleep once
            mock_sleep.assert_called_once()
            self.assertEqual(mock_client.models.generate_content.call_count, 2)
            self.assertEqual(result.plot.width, 10)

    @patch('app.services.ai.prompt_builder.build_prompt', return_value="prompt")
    @patch('google.genai.Client')
    def test_repeated_503_exhausts_retries(self, mock_client_cls, mock_build):
        mock_client = MagicMock()
        self.provider.client = mock_client
        
        mock_client.models.generate_content.side_effect = Exception("503 UNAVAILABLE")
        
        with patch('time.sleep') as mock_sleep:
            with self.assertRaises(RuntimeError) as context:
                self.provider.generate_layout({})
                
            self.assertEqual(mock_sleep.call_count, 2)
            self.assertEqual(mock_client.models.generate_content.call_count, 3)
            self.assertIn("AI service is temporarily busy. Please try again shortly.", str(context.exception))

    @patch('app.services.ai.prompt_builder.build_prompt', return_value="prompt")
    @patch('google.genai.Client')
    def test_auth_error_not_retried(self, mock_client_cls, mock_build):
        mock_client = MagicMock()
        self.provider.client = mock_client
        
        mock_client.models.generate_content.side_effect = Exception("API key not valid")
        
        with patch('time.sleep') as mock_sleep:
            with self.assertRaises(RuntimeError) as context:
                self.provider.generate_layout({})
                
            mock_sleep.assert_not_called()
            self.assertEqual(mock_client.models.generate_content.call_count, 1)
            self.assertIn("PROVIDER_AUTH_ERROR", str(context.exception))
            
    @patch('app.services.ai.prompt_builder.build_prompt', return_value="prompt")
    @patch('google.genai.Client')
    def test_schema_400_not_retried(self, mock_client_cls, mock_build):
        mock_client = MagicMock()
        self.provider.client = mock_client
        
        mock_client.models.generate_content.side_effect = Exception("400 INVALID_ARGUMENT schema")
        
        with patch('time.sleep') as mock_sleep:
            with self.assertRaises(RuntimeError) as context:
                self.provider.generate_layout({})
                
            mock_sleep.assert_not_called()
            self.assertEqual(mock_client.models.generate_content.call_count, 1)
            self.assertIn("PROVIDER_SCHEMA_ERROR", str(context.exception))

if __name__ == '__main__':
    unittest.main()
