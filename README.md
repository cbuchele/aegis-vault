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

## 🚀 Publishing to PyPI

1. **Update Version**: Bump the version in `aegis_vault/__init__.py`

2. **Build the package**:
   ```bash
   pip install --upgrade build twine
   python -m build
   ```

3. **Test the build**:
   ```bash
   python -m twine upload --repository testpypi dist/*
   pip install --index-url https://test.pypi.org/simple/ --no-deps aegis-vault
   ```

4. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

5. **Verify installation**:
   ```bash
   pip install aegis-vault
   python -c "from aegis_vault import VaultGPT; print('Aegis Vault installed successfully!')"
   ```

## 🛠 Development

```bash
# Clone the repository
git clone https://github.com/yourusername/aegis-vault.git
cd aegis-vault

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
