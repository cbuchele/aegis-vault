# Aegis Vault 🛡️

[![PyPI version](https://img.shields.io/pypi/v/aegis-vault.svg)](https://pypi.org/project/aegis-vault/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/pypi/pyversions/aegis-vault.svg)](https://pypi.org/project/aegis-vault/)

Secure, LGPD-compliant middleware for protecting sensitive data in LLM prompts. Aegis Vault automatically detects, redacts, and encrypts sensitive information before it reaches LLM APIs, ensuring compliance with data protection regulations.

## ✨ Features

- 🔍 Automatic detection of sensitive data (CPF, CNPJ, emails, etc.)
- 🔒 Secure encryption of sensitive information
- 🛡️ Protection against prompt injection and data leaks
- 🔄 Easy restoration of original content in LLM responses
- 🚀 Simple integration with any LLM workflow
- 🇧🇷 Optimized for Brazilian data protection (LGPD)

## 🔐 What It Does

Aegis Vault provides a secure middleware layer between your application and LLMs:

- **Detects sensitive data** using regex patterns and NER (Named Entity Recognition)
- **Redacts and encrypts** PII before sending to LLMs
- **Securely stores** encrypted data in a local vault
- **Restores redacted content** in LLM responses
- **Blocks malicious inputs** including prompt injection and DoS patterns
- **LGPD-compliant** with special focus on Brazilian Portuguese data

## 📦 Installation

Install using pip:

```bash
pip install aegis-vault
```

For development with additional tools:

```bash
pip install 'aegis-vault[dev]'
```

## 🚀 Quick Start

### Basic Usage with System Prompts

When integrating with LLMs, it's crucial to include a system prompt that instructs the model to preserve vault markers. Here's how to do it:

```python
from aegis_vault import VaultGPT

# Initialize with a custom system prompt
vault = VaultGPT(
    encryption_key="your-secure-key",
    system_prompt="""
    You are processing text with sensitive information.
    
    IMPORTANT: Preserve all <<VAULT_X>> markers exactly as they appear.
    Never modify, remove, or reorder these markers in your responses.
    """.strip()
)

def query_llm(prompt, system_prompt=None):
    """Example function to call an LLM API"""
    # In a real implementation, you would call your LLM API here
    # For example, with OpenAI:
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": system_prompt or ""},
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    # return response.choices[0].message['content']
    
    # For demonstration, just return a mock response
    return f"Processed your request. Detected sensitive data: {prompt}"

# The secure_chat method will automatically handle redaction and restoration
response = vault.secure_chat(
    "My email is user@example.com and my SSN is 123-45-6789",
    query_llm
)
print(response)
```

### Basic Usage

```python
from aegis_vault import VaultGPT

# Initialize the vault with default settings
vault = VaultGPT()

# Process a prompt securely
def my_llm_function(prompt):
    # This is where you would call your actual LLM
    return f"Processed: {prompt}"

# Sensitive data will be automatically detected and protected
response = vault.secure_chat(
    "Meu CPF é 123.456.789-00 e meu email é usuario@exemplo.com.br",
    my_llm_function
)

print(response)
# Output: Processed: Meu CPF é 123.456.789-00 e meu email é usuario@exemplo.com.br
```

### Advanced Usage

```python
from aegis_vault import VaultGPT

# Initialize with custom encryption key
vault = VaultGPT(encryption_key="my-secret-key-123")

# Redact sensitive information from text
redacted = vault.redact_prompt(
    "Por favor, envie um email para usuario@exemplo.com informando sobre o CPF 123.456.789-00"
)
print(f"Redacted: {redacted}")
# Output: Redacted: Por favor, envie um email para <<VAULT_0>> informando sobre o CPF <<VAULT_1>>

# Restore original content
restored = vault.restore_content(redacted)
print(f"Restored: {restored}")
# Output: Restored: Por favor, envie um email para usuario@exemplo.com informando sobre o CPF 123.456.789-00
```

## 📚 Usage Guide

### System Prompt Best Practices

When working with LLMs, it's important to include clear instructions about handling vault markers. Here's a recommended approach:

1. **Be Explicit**: Clearly state that the markers (`<<VAULT_X>>`) are special and must be preserved
2. **Provide Clear Rules**: Give specific instructions about not modifying, removing, or reordering the markers
3. **Include Examples**: Show examples of correct and incorrect behavior
4. **Make it Stand Out**: Use formatting (like ALL CAPS or emojis) to draw attention to these instructions

Example system prompt:

```python
system_prompt = """
You are a helpful assistant that processes text containing sensitive information.

IMPORTANT: The user's message may contain special markers like <<VAULT_0>>, <<VAULT_1>>, etc.
These markers represent redacted sensitive information.

RULES:
1. NEVER modify, remove, or reorder these markers in your response
2. Return all markers exactly as they appear in the input
3. If you need to refer to the redacted content, use the marker itself
4. Do not try to guess what the markers represent
5. If unsure, respond with the markers unchanged
""".strip()

vault = VaultGPT(system_prompt=system_prompt)
```

### Initialization Options

```python
from aegis_vault import VaultGPT

# Basic initialization (auto-generates encryption key)
vault = VaultGPT()

# With custom encryption key
vault = VaultGPT(encryption_key="your-32-char-secret-key")

# Disable NER for better performance if not needed
vault = VaultGPT(use_ner=False)

# Lazy load spaCy model (load only when needed)
vault = VaultGPT(load_spacy=False)
# Later, when needed:
# vault._load_spacy_model("pt_core_news_sm")
```

### Secure Chat Integration

```python
def query_llm(prompt):
    """Example function to simulate LLM API call"""
    # In a real scenario, this would call your LLM API
    return f"LLM Response to: {prompt}"

# Process sensitive prompts securely
response = vault.secure_chat(
    "Meus dados são: CPF 123.456.789-00, email: usuario@exemplo.com",
    query_llm
)
print(response)
```

### Advanced Features

#### Custom Patterns

```python
# Add custom patterns for sensitive data
vault.PATTERNS['credit_card'] = r'\b(?:\d[ -]*?){13,16}\b'

# Add custom malicious patterns to block
vault.MALICIOUS_PATTERNS.append(r'shutdown\s+computer')
```

#### Vault Management

```python
# Export vault data (can include encryption key if needed)
json_data = vault.export_vault(include_key=False)  # Don't include key in exports by default

# Save vault to file (encrypted)
vault.save_vault_to_file("secure_vault.json", include_key=False)

# Load vault from file
new_vault = VaultGPT()
new_vault.load_vault_from_file("secure_vault.json")
# Note: You'll need to set the encryption key separately if it wasn't included
```

## 💡 Use Cases

- **Healthcare**: Protect patient data in medical AI applications
- **Finance**: Secure financial information in banking chatbots
- **Legal**: Ensure client confidentiality in legal document processing
- **Customer Support**: Protect customer information in support chatbots
- **Enterprise**: Maintain LGPD compliance in corporate AI systems


## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
