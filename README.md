

Aegis Vault 🛡️
Secure, LGPD-compliant middleware for protecting sensitive data in LLM prompts. Aegis Vault automatically detects, redacts, and encrypts sensitive information before it reaches LLM APIs, ensuring compliance with data protection regulations.

✨ Features
🔍 Automatic detection of sensitive data (CPF, CNPJ, emails, etc.)
🔒 Secure encryption of sensitive information
🛡️ Protection against prompt injection and data leaks
🔄 Easy restoration of original content in LLM responses
🚀 Simple integration with any LLM workflow
🇧🇷 Optimized for Brazilian data protection (LGPD)
🔐 What It Does
Aegis Vault provides a secure middleware layer between your application and LLMs:

Detects sensitive data using regex patterns and NER (Named Entity Recognition)
Redacts and encrypts PII before sending to LLMs
Securely stores encrypted data in a local vault
Restores redacted content in LLM responses
Blocks malicious inputs including prompt injection and DoS patterns
LGPD-compliant with special focus on Brazilian Portuguese data
📦 Installation
Install using pip:

Bash

pip install aegis-vault
🚀 Quick Start
Basic Usage
Python

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
Advanced Usage
Python

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
📚 Usage Guide
Initialization Options
Python

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
Secure Chat Integration
Python

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
Advanced Features
Custom Patterns
Python

# Add custom patterns for sensitive data
vault.PATTERNS['credit_card'] = r'\b(?:\d[ -]*?){13,16}\b'

# Add custom malicious patterns to block
vault.MALICIOUS_PATTERNS.append(r'shutdown\s+computer')
Vault Management
Python

# Export vault data (can include encryption key if needed)
json_data = vault.export_vault(include_key=False)  # Don't include key in exports by default

# Save vault to file (encrypted)
vault.save_vault_to_file("secure_vault.json", include_key=False)

# Load vault from file
new_vault = VaultGPT()
new_vault.load_vault_from_file("secure_vault.json")
# Note: You'll need to set the encryption key separately if it wasn't included
💡 Use Cases
Healthcare: Protect patient data in medical AI applications
Finance: Secure financial information in banking chatbots
Legal: Ensure client confidentiality in legal document processing
Customer Support: Protect customer information in support chatbots
Enterprise: Maintain LGPD compliance in corporate AI systems


You can find my Linktree here: https://linktr.ee/cbuchele?utm_source=linktree_admin_share.

About Me & Aegis AI

I'm Carlos, a Full Stack Developer, Offensive Security Specialist, Python Developer, and LLM/AI Specialist. I am the creator of Aegis Vault and the company Aegis AI.

Aegis AI specializes in applying custom LLM model solutions to businesses in the modern world. We create chat assistants for all business sectors, with qualified filters for correct data privacy laws. As a cybersecurity company, we also offer audits to ensure you're in compliance, as well as review your existing code for vulnerabilities or outdated code. Our broader cybersecurity services include professional security audits, penetration testing (including gamified LLM pentesting with our Merlin CTF challenges), security training and certifications, red team operations, code review, hardening, and incident response. We are committed to enhancing digital security and provide open and free access to many of our courses, including our AI-Powered Threat Detection course. Be on the lookout for our upcoming new free courses and trainings!
