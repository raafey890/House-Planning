import unittest
from unittest.mock import patch, MagicMock
from app.services.ai.gemini_provider import GeminiProvider

class TestGeminiFallback(unittest.TestCase):
    def setUp(self):
        self.provider = GeminiProvider()
        
    @patch('app.services.ai.prompt_builder.build_prompt', return_value="prompt")
    @patch('google.genai.Client')
    def test_primary_succeeds(self, mock_client_cls, mock_build):
        mock_client = MagicMock()
        self.provider.client = mock_client
        mock_response = MagicMock()
        mock_response.text = '{"schema_version": "1.0", "units": "ft", "plot": {"width": 10, "length": 10, "facing": "North", "buildable_boundary": {"width": 8, "length": 8}, "setbacks": {}}}'
        
        mock_client.models.generate_content.return_value = mock_response
        
        with patch('time.sleep') as mock_sleep:
            result = self.provider.generate_layout({})
            mock_sleep.assert_not_called()
            
            # Check model name passed
            call_args = mock_client.models.generate_content.call_args[1]
            self.assertEqual(call_args['model'], "gemini-3.8-flash")
            self.assertEqual(mock_client.models.generate_content.call_count, 1)

    @patch('app.services.ai.prompt_builder.build_prompt', return_value="prompt")
    @patch('google.genai.Client')
    def test_primary_exhausted_fallback_succeeds(self, mock_client_cls, mock_build):
        mock_client = MagicMock()
        self.provider.client = mock_client
        mock_response = MagicMock()
        mock_response.text = '{"schema_version": "1.0", "units": "ft", "plot": {"width": 10, "length": 10, "facing": "North", "buildable_boundary": {"width": 8, "length": 8}, "setbacks": {}}}'
        
        # Primary fails 3 times, fallback succeeds on 1st time
        mock_client.models.generate_content.side_effect = [
            Exception("503 UNAVAILABLE 1"),
            Exception("503 UNAVAILABLE 2"),
            Exception("503 UNAVAILABLE 3"),
            mock_response
        ]
        
        with patch('time.sleep') as mock_sleep:
            result = self.provider.generate_layout({})
            
            self.assertEqual(mock_client.models.generate_content.call_count, 4)
            # Sleep should be called twice for the primary 3 attempts
            self.assertEqual(mock_sleep.call_count, 2)
            
            calls = mock_client.models.generate_content.call_args_list
            self.assertEqual(calls[0][1]['model'], "gemini-3.8-flash")
            self.assertEqual(calls[1][1]['model'], "gemini-3.8-flash")
            self.assertEqual(calls[2][1]['model'], "gemini-3.8-flash")
            self.assertEqual(calls[3][1]['model'], "gemini-3.7-flash")

    @patch('app.services.ai.prompt_builder.build_prompt', return_value="prompt")
    @patch('google.genai.Client')
    def test_primary_auth_error_no_fallback(self, mock_client_cls, mock_build):
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
    def test_primary_schema_error_no_fallback(self, mock_client_cls, mock_build):
        mock_client = MagicMock()
        self.provider.client = mock_client
        
        mock_client.models.generate_content.side_effect = Exception("400 INVALID_ARGUMENT schema")
        
        with patch('time.sleep') as mock_sleep:
            with self.assertRaises(RuntimeError) as context:
                self.provider.generate_layout({})
                
            mock_sleep.assert_not_called()
            self.assertEqual(mock_client.models.generate_content.call_count, 1)
            self.assertIn("PROVIDER_SCHEMA_ERROR", str(context.exception))
            
    @patch('app.services.ai.prompt_builder.build_prompt', return_value="prompt")
    @patch('google.genai.Client')
    def test_primary_and_fallback_fail(self, mock_client_cls, mock_build):
        mock_client = MagicMock()
        self.provider.client = mock_client
        
        # Primary fails 3 times, fallback fails 2 times
        mock_client.models.generate_content.side_effect = [
            Exception("503 UNAVAILABLE 1"),
            Exception("503 UNAVAILABLE 2"),
            Exception("503 UNAVAILABLE 3"),
            Exception("503 UNAVAILABLE 4"),
            Exception("503 UNAVAILABLE 5"),
        ]
        
        with patch('time.sleep') as mock_sleep:
            with self.assertRaises(RuntimeError) as context:
                self.provider.generate_layout({})
                
            self.assertEqual(mock_client.models.generate_content.call_count, 5)
            # Sleep twice for primary, once for fallback = 3
            self.assertEqual(mock_sleep.call_count, 3)
            self.assertIn("AI service is temporarily busy. Please try again shortly.", str(context.exception))

if __name__ == '__main__':
    unittest.main()
