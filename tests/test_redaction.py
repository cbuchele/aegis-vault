"""
Tests for the redaction and restoration functionality of VaultGPT.
"""

import unittest
import re
from aegis_vault import VaultGPT


class TestRedaction(unittest.TestCase):
    """Test suite for VaultGPT redaction functionality."""
    
    def setUp(self):
        """Set up a VaultGPT instance for testing."""
        self.vault = VaultGPT(encryption_key="test-key", load_spacy=False)
    
    def test_cpf_redaction(self):
        """Test that CPF numbers are properly redacted."""
        # Test with formatted CPF
        prompt = "Meu CPF é 123.456.789-00 e preciso de ajuda."
        redacted = self.vault.redact_prompt(prompt)
        
        # Check that the CPF is redacted
        self.assertNotIn("123.456.789-00", redacted)
        # Check that a vault token is present
        self.assertTrue(re.search(r'<<VAULT_\d+>>', redacted))
        
        # Test with unformatted CPF
        prompt = "Meu CPF é 12345678900 e preciso de ajuda."
        redacted = self.vault.redact_prompt(prompt)
        
        # Check that the CPF is redacted
        self.assertNotIn("12345678900", redacted)
    
    def test_email_redaction(self):
        """Test that email addresses are properly redacted."""
        prompt = "Meu email é usuario@exemplo.com.br e preciso de ajuda."
        redacted = self.vault.redact_prompt(prompt)
        
        # Check that the email is redacted
        self.assertNotIn("usuario@exemplo.com.br", redacted)
        # Check that a vault token is present
        self.assertTrue(re.search(r'<<VAULT_\d+>>', redacted))
    
    def test_multiple_pii_redaction(self):
        """Test that multiple PII items are properly redacted."""
        prompt = "Meu nome é João Silva, CPF 123.456.789-00, email joao@exemplo.com.br."
        redacted = self.vault.redact_prompt(prompt)
        
        # Check that PII is redacted
        self.assertNotIn("123.456.789-00", redacted)
        self.assertNotIn("joao@exemplo.com.br", redacted)
        
        # Check number of vault tokens (should be at least 2)
        tokens = re.findall(r'<<VAULT_\d+>>', redacted)
        self.assertGreaterEqual(len(tokens), 2)
    
    def test_restoration(self):
        """Test that redacted content can be properly restored."""
        original = "Meu CPF é 123.456.789-00 e meu email é usuario@exemplo.com.br."
        redacted = self.vault.redact_prompt(original)
        restored = self.vault.restore_content(redacted)
        
        # Check that the restored text matches the original
        self.assertEqual(original, restored)
    
    def test_llm_flow(self):
        """Test the complete secure_chat flow with a mock LLM."""
        def mock_llm(prompt):
            """Mock LLM that echoes the prompt."""
            return f"Recebi: {prompt}"
        
        original = "Meu CPF é 123.456.789-00 e preciso de ajuda."
        response = self.vault.secure_chat(original, mock_llm)
        
        # Check that the response doesn't contain the vault token
        self.assertNotIn("<<VAULT_", response)
        # Check that the original CPF is in the response (it was restored)
        self.assertIn("123.456.789-00", response)
    
    def test_malicious_content_blocking(self):
        """Test that malicious content is blocked."""
        malicious_prompt = "rm -rf / --no-preserve-root"
        response = self.vault.secure_chat(malicious_prompt, lambda p: "This shouldn't be called")
        
        # Check that the response indicates blocking
        self.assertIn("blocked for security reasons", response)


if __name__ == '__main__':
    unittest.main()
