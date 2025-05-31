"""
Middleware for secure, LGPD-compliant LLM prompt protection.

This module provides the VaultGPT class, which detects, redacts, and encrypts
sensitive data in prompts before sending them to LLMs.
"""

import re
import json
import base64
import logging
import os
from typing import Dict, List, Callable, Any, Optional, Tuple, Union
import warnings

try:
    import spacy
    from spacy.language import Language
except ImportError:
    warnings.warn("spaCy not installed. NER detection will not be available.")
    spacy = None

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class VaultGPT:
    """
    VaultGPT: Secure middleware for LLM prompt protection.
    
    Detects, redacts, and encrypts sensitive data in prompts before sending
    them to LLMs, with protections against malicious input, injection, and
    denial-of-service patterns.
    """
    
    # Regex patterns for common PII in Portuguese (Brazil)
    PATTERNS = {
        'CPF': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
        'CNPJ': r'\d{2}\.?\d{3}\.?\d{3}/?0001-?\d{2}',
        'RG': r'(\d{1,2}\.?\d{3}\.?\d{3}-?[0-9X])',
        'BIRTHDATE': r'\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}\b',
        'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'PHONE': r'(?:\+55\s?)?(?:\(?\d{2}\)?[\s-]?)?\d{4,5}[-\s]?\d{4}',
        'IP_ADDRESS': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'API_KEY': r'(?:api[_-]?key|token)[_-]?(?:\w{8,})',
        'ADDRESS': r'\b(?:Rua|Av|Avenida|Alameda|Al|Travessa|Rodovia)[\w\s\.,]+\d+\b',
    }
    
    # Malicious patterns to detect
    MALICIOUS_PATTERNS = [
        r'rm\s+-rf',
        r'while\s*\(\s*true\s*\)',
        r'while\s*true',
        r'for\s*\(\s*;;\s*\)',
        r':\(\)\{\s*:\|\:&\s*\};:',  # Fork bomb
        r'<script>',
        r'eval\s*\(',
        r'system\s*\(',
        r'exec\s*\(',
        r'sudo',
        r'chmod\s+777',
    ]
    
    # Maximum prompt size (500,000 characters)
    MAX_PROMPT_SIZE = 500_000
    
    def __init__(
        self,
        encryption_key: Optional[str] = None,
        use_ner: bool = True,
        load_spacy: bool = True,
        spacy_model: str = "pt_core_news_sm",
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the Vault with optional encryption key and NER settings.

        Args:
            encryption_key: Optional encryption key. If not provided, a random key will be generated.
            use_ner: Whether to use spaCy NER for entity recognition.
            load_spacy: Whether to load the spaCy model on initialization.
            spacy_model: Name of the spaCy model to use.
            system_prompt: Optional custom system prompt to instruct the LLM about vault markers.
                         If None, a default prompt will be used.
        """
        self.encryption_key = encryption_key or Fernet.generate_key().decode()
        self.cipher_suite = Fernet(self.encryption_key.encode())
        self.vault = {}
        self.token_counter = 0
        self.use_ner = use_ner
        self.nlp = None
        self.spacy_model = spacy_model
        
        # System prompt to preserve vault markers in LLM responses
        self.default_system_prompt = """
You will receive input containing placeholder markers such as <<VAULT_0>>, <<VAULT_1>>, etc. These markers represent redacted sensitive information.

⚠️ IMPORTANT INSTRUCTIONS:

- DO NOT attempt to guess or replace what any <<VAULT_X>> marker represents.
- You MAY reference and use these markers in new positions or sentence structures, but you must ALWAYS use the markers exactly as provided (e.g., <<VAULT_0>>).
- NEVER rename, alter, reformat, paraphrase, or omit any marker.
- Responses should be coherent and context-aware, but the markers must remain intact and clearly preserved wherever referenced.

These markers will be programmatically replaced after your response. Treat them as untouchable placeholders for confidential content.
""".strip()
        
        self.system_prompt = system_prompt or self.default_system_prompt
        
        if use_ner and load_spacy:
            self._load_spacy_model()
    
    def _load_spacy_model(self) -> None:
        """
        Load the specified spaCy model.
        
        Args:
            model_name: Name of the spaCy model to load
        """
        try:
            self.nlp = spacy.load(self.spacy_model)
            logging.info(f"Loaded spaCy model: {self.spacy_model}")
        except OSError:
            logging.warning(f"Model {self.spacy_model} not found. Downloading...")
            try:
                os.system(f"python -m spacy download {self.spacy_model}")
                self.nlp = spacy.load(self.spacy_model)
                logging.info(f"Downloaded and loaded spaCy model: {self.spacy_model}")
            except Exception as e:
                logging.error(f"Failed to download spaCy model: {e}")
                self.use_ner = False
    
    def _derive_key(self, password: str) -> bytes:
        """
        Derive a secure key from a password.
        
        Args:
            password: Password to derive key from
            
        Returns:
            bytes: Derived key
        """
        salt = b'aegis-vault-secure-salt'  # In production, use a secure random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _encrypt(self, text: str) -> str:
        """
        Encrypt text using Fernet (AES).
        
        Args:
            text: Text to encrypt
            
        Returns:
            str: Encrypted text (base64)
        """
        encrypted = self.cipher_suite.encrypt(text.encode())
        return encrypted.decode()
    
    def _decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt text using Fernet (AES).
        
        Args:
            encrypted_text: Encrypted text to decrypt
            
        Returns:
            str: Decrypted text
        """
        decrypted = self.cipher_suite.decrypt(encrypted_text.encode())
        return decrypted.decode()
    
    def _detect_regex_pii(self, text: str) -> List[Tuple[str, str, int, int]]:
        """
        Detect PII using regex patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of tuples (entity_type, entity_text, start_pos, end_pos)
        """
        detected = []
        
        for entity_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text):
                detected.append((
                    entity_type,
                    match.group(),
                    match.start(),
                    match.end()
                ))
        
        return detected
    
    def _detect_ner_entities(self, text: str) -> List[Tuple[str, str, int, int]]:
        """
        Detect entities using spaCy NER.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of tuples (entity_type, entity_text, start_pos, end_pos)
        """
        if not self.use_ner or not self.nlp:
            return []
        
        detected = []
        doc = self.nlp(text)
        
        for ent in doc.ents:
            detected.append((
                ent.label_,
                ent.text,
                ent.start_char,
                ent.end_char
            ))
        
        return detected
    
    def _looks_malicious(self, prompt: str) -> bool:
        """
        Check if a prompt looks malicious.
        
        Args:
            prompt: Prompt to check
            
        Returns:
            bool: True if prompt looks malicious
        """
        # Check for excessive size
        if len(prompt) > self.MAX_PROMPT_SIZE:
            logging.warning(f"Prompt exceeds maximum size: {len(prompt)} > {self.MAX_PROMPT_SIZE}")
            return True
        
        # Check for malicious patterns
        for pattern in self.MALICIOUS_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                logging.warning(f"Malicious pattern detected: {pattern}")
                return True
        
        # Check for excessive repetition (potential DoS)
        repetition_threshold = 100
        for length in range(10, 100):
            for i in range(len(prompt) - length):
                substring = prompt[i:i+length]
                if prompt.count(substring) > repetition_threshold:
                    logging.warning(f"Excessive repetition detected: {substring[:20]}...")
                    return True
        
        return False
    
    def redact_prompt(self, prompt: str) -> str:
        """
        Redact sensitive information from a prompt.
        
        Args:
            prompt: Original prompt
            
        Returns:
            str: Redacted prompt with vault tokens
        """
        # Reset token counter if vault is empty
        if not self.vault:
            self.token_counter = 0
        
        # Make a copy of the prompt to modify
        redacted = prompt
        
        # Find all matches for each pattern
        for pattern_name, pattern in self.PATTERNS.items():
            # Reset the match position for each pattern
            offset = 0
            
            # Find all matches in the current redacted prompt
            for match in re.finditer(pattern, redacted):
                # Get the matched text and its position
                matched_text = match.group()
                start = match.start()
                
                # Create a token
                token = f"<<VAULT_{self.token_counter}>>"
                
                # Store the exact match and its position
                self.vault[self.token_counter] = {
                    'type': pattern_name,
                    'value': self._encrypt(matched_text),
                    'original': matched_text
                }
                
                # Replace the matched text with the token
                redacted = redacted[:start + offset] + token + redacted[start + len(matched_text) + offset:]
                
                # Update the offset for subsequent replacements
                offset += len(token) - len(matched_text)
                
                self.token_counter += 1
        
        return redacted
    
    def restore_content(self, text: str) -> str:
        """
        Restore redacted content from vault tokens.
        
        Args:
            text: Text with vault tokens
            
        Returns:
            str: Text with sensitive data restored
        """
        restored = text
        
        # Find all tokens in the text
        tokens = list(re.finditer(r'<<VAULT_(\d+)>>', restored))
        
        # Process tokens from last to first to avoid offset issues
        for match in reversed(tokens):
            token_id = int(match.group(1))
            if token_id in self.vault:
                # Get the original value
                if 'original' in self.vault[token_id]:
                    original = self.vault[token_id]['original']
                else:  # For backward compatibility
                    encrypted = self.vault[token_id]['value']
                    original = self._decrypt(encrypted)
                
                # Replace the token with the original value
                start, end = match.span()
                restored = restored[:start] + original + restored[end:]
        
        return restored
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt that should be sent to the LLM.
        
        Returns:
            str: The system prompt to preserve vault markers
        """
        return self.system_prompt
    
    def set_system_prompt(self, prompt: Optional[str] = None) -> None:
        """
        Set a custom system prompt or reset to default.
        
        Args:
            prompt: Custom system prompt. If None, resets to default.
        """
        self.system_prompt = prompt or self.default_system_prompt
    
    def secure_chat(
        self, 
        prompt: str, 
        llm_function: Callable[[str], str],
        include_system_prompt: bool = True,
        **llm_kwargs
    ) -> str:
        """
        Process a prompt through the LLM while protecting sensitive data.

        Args:
            prompt: The user's input prompt
            llm_function: A function that takes a string and returns the LLM's response.
                         For chat models, this function should handle system prompts.
            include_system_prompt: Whether to include the system prompt (default: True).
                                Set to False if you're handling system prompts manually.
            **llm_kwargs: Additional arguments to pass to the LLM function.

        Returns:
            The LLM's response with sensitive data restored
            
        Example with OpenAI's chat completion:
            ```python
            def openai_chat(prompt):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": vault.get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message['content']
                
            response = vault.secure_chat("My SSN is 123-45-6789", openai_chat)
            ```
        """
        # Redact sensitive information
        redacted_prompt = self.redact_prompt(prompt)
        
        # Include system prompt if needed (for chat models)
        if include_system_prompt and hasattr(llm_function, '__code__') and 'system_prompt' in llm_function.__code__.co_varnames:
            llm_kwargs['system_prompt'] = self.system_prompt
        
        # Get LLM response
        llm_response = llm_function(redacted_prompt, **llm_kwargs)
        
        # Restore original content in the response
        restored_response = self.restore_content(llm_response)
        
        return restored_response
    
    def export_vault(self, include_key: bool = False) -> str:
        """
        Export the vault to a JSON string.
        
        Args:
            include_key: Whether to include the encryption key
            
        Returns:
            str: JSON string with vault data
        """
        export_data = {
            'vault': self.vault,
            'token_counter': self.token_counter
        }
        
        if include_key:
            export_data['encryption_key'] = self.encryption_key.decode()
            warnings.warn("Exporting with encryption key. Keep this secure!")
        
        return json.dumps(export_data)
    
    def load_vault(self, json_string: str) -> None:
        """
        Load vault from a JSON string.
        
        Args:
            json_string: JSON string with vault data
        """
        import_data = json.loads(json_string)
        
        self.vault = import_data['vault']
        self.token_counter = import_data['token_counter']
        
        if 'encryption_key' in import_data:
            self.encryption_key = import_data['encryption_key'].encode()
            self.cipher = Fernet(self.encryption_key)
    
    def save_vault_to_file(self, filename: str, include_key: bool = False) -> None:
        """
        Save vault to a file.
        
        Args:
            filename: Path to save file
            include_key: Whether to include the encryption key
        """
        with open(filename, 'w') as f:
            f.write(self.export_vault(include_key))
    
    def load_vault_from_file(self, filename: str) -> None:
        """
        Load vault from a file.
        
        Args:
            filename: Path to load file from
        """
        with open(filename, 'r') as f:
            self.load_vault(f.read())
