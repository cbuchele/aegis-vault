# 🛡️ Aegis Vault

**Secure, LGPD-compliant middleware for protecting sensitive data in LLM prompts.**

Aegis Vault automatically detects, redacts, and encrypts sensitive information before it reaches LLM APIs, ensuring compliance with data protection regulations.

---

## ✨ Features

- 🔍 Automatic detection of sensitive data (CPF, CNPJ, emails, etc.)
- 🔒 Secure encryption of sensitive information
- 🛡️ Protection against prompt injection and data leaks
- 🔄 Easy restoration of original content in LLM responses
- 🚀 Simple integration with any LLM workflow
- 🇧🇷 Optimized for Brazilian data protection (LGPD)

- **upcoming updates ( Add all regex for PII IE credit cards etc )

---

## 🔐 What It Does

Aegis Vault provides a secure middleware layer between your application and LLMs:

- Detects sensitive data using regex patterns and NER (Named Entity Recognition)
- Redacts and encrypts PII before sending to LLMs
- Securely stores encrypted data in a local vault
- Restores redacted content in LLM responses
- Blocks malicious inputs including prompt injection and DoS patterns
- LGPD-compliant with special focus on Brazilian Portuguese data

---

## 📦 Installation

```bash
pip install aegis-vault
```

---

## 🚀 Quick Start

### Basic Usage

```python
from aegis_vault import VaultGPT

# Initialize the vault
vault = VaultGPT()

# Define your LLM function
def my_llm_function(prompt):
    return f"Processed: {prompt}"

# Process sensitive data securely
response = vault.secure_chat(
    "Meu CPF é 123.456.789-00 e meu email é usuario@exemplo.com.br",
    my_llm_function
)

print(response)
```

**Output:**
```
Processed: Meu CPF é 123.456.789-00 e meu email é usuario@exemplo.com.br
```

---

### Advanced Usage

```python
from aegis_vault import VaultGPT

# Initialize with custom encryption key
vault = VaultGPT(encryption_key="my-secret-key-123") #Fernet encryption key needs to be a 32-byte URL-safe base64-encoded string

# Redact sensitive information
redacted = vault.redact_prompt(
    "Por favor, envie um email para usuario@exemplo.com informando sobre o CPF 123.456.789-00"
)
print(f"Redacted: {redacted}")
```

**Output:**
```
Redacted: Por favor, envie um email para <<VAULT_0>> informando sobre o CPF <<VAULT_1>>
```

```python
# Restore original content
restored = vault.restore_content(redacted)
print(f"Restored: {restored}")
```

**Output:**
```
Restored: Por favor, envie um email para usuario@exemplo.com informando sobre o CPF 123.456.789-00
```

---

## 📚 Usage Guide

### Initialization Options

```python
# Basic initialization
vault = VaultGPT()

# With custom encryption key
vault = VaultGPT(encryption_key="your-32-char-secret-key")

# Disable NER for performance
vault = VaultGPT(use_ner=False)

# Lazy load spaCy model
vault = VaultGPT(load_spacy=False)
vault._load_spacy_model("pt_core_news_sm")
```

---

### Secure Chat Integration

```python
def query_llm(prompt):
    return f"LLM Response to: {prompt}"

response = vault.secure_chat(
    "Meus dados são: CPF 123.456.789-00, email: usuario@exemplo.com",
    query_llm
)
print(response)
```

---

### Custom Patterns

```python
# Add custom pattern for credit cards
vault.PATTERNS['credit_card'] = r'\b(?:\d[ -]*?){13,16}\b'

# Add custom malicious prompt pattern
vault.MALICIOUS_PATTERNS.append(r'shutdown\s+computer')
```

---

### Vault Management

```python
# Export vault as JSON
json_data = vault.export_vault(include_key=False)

# Save to file (encrypted)
vault.save_vault_to_file("secure_vault.json", include_key=False)

# Load from file
new_vault = VaultGPT()
new_vault.load_vault_from_file("secure_vault.json")
```

> ⚠️ Note: You must set the encryption key separately if it wasn’t included in the vault export.

---

## 💡 Use Cases

- **Healthcare**: Protect patient data in AI-powered medical tools  
- **Finance**: Secure financial identifiers in banking applications  
- **Legal**: Ensure confidentiality in legal document LLM workflows  
- **Customer Support**: Redact and reinsert PII in automated agents  
- **Enterprise**: Comply with LGPD across corporate LLM deployments




---

## 🛡️ Example: Shielding OpenAI and Gemini APIs with Aegis Vault

When working with LLM APIs like OpenAI and Google Gemini, it's critical to prevent sensitive personal data (e.g. CPF, email, address) from being sent unprotected. Aegis Vault acts as a middleware filter that sanitizes, encrypts, and safely restores this data in responses.

---

### 🔐 Using with OpenAI API

```python
import openai
from aegis_vault import VaultGPT

vault = VaultGPT()

# Example function to proxy OpenAI securely
def call_openai(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message["content"]

# Secure call
prompt = "Meu CPF é 123.456.789-00 e meu email é joao@email.com.br. Crie um contrato simples."
secure_response = vault.secure_chat(prompt, call_openai)

print(secure_response)
```

✅ This ensures OpenAI never sees sensitive data in the prompt.

---

### 🧠 Using with Gemini Pro API (REST)

```python
import requests
from aegis_vault import VaultGPT

vault = VaultGPT()

def call_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# Example with sensitive info
prompt = "Contrato para João da Silva, CPF 987.654.321-00, cliente da empresa XYZ."

secure_response = vault.secure_chat(prompt, call_gemini)

print(secure_response)
```

---

### 💡 Why This Matters

Without this layer, prompts could leak:

- 💥 LGPD-protected information (CPF, name, address, emails)
- 💣 Secrets like credentials, tokens, or business logic
- 📉 Regulatory exposure from storing logs with PII

Using `Aegis Vault` means:

- ✅ No raw PII is ever sent to external APIs
- ✅ You maintain full compliance with Brazilian and international privacy laws
- ✅ You gain control over what gets sent and returned

---

📦 Try integrating Aegis Vault into your AI gateway, chatbot, legal assistant, or support bot — anywhere sensitive data flows through LLM prompts.

---

## 👨‍💻 About Me & Aegis AI

I'm **Carlos**, a Full Stack Developer, Offensive Security Specialist, Python Engineer, and LLM/AI expert.

I’m the creator of Aegis Vault and the founder of **[Aegis AI](https://aegisai.com.br)** — a startup with teams in Brazil and the US.  
We specialize in secure LLM software, AI agents, custom deployments, and cybersecurity audits.

We offer:

- Custom AI assistant development  
- LGPD/GDPR-compliant AI workflows  
- Pentesting (including gamified LLM CTFs with our tool Merlin)  
- Security audits, hardening, and training  
- A growing library of open-source tools & courses  

📚 Check out our free course: *AI-Powered Threat Detection*  
🧩 Linktree: [https://linktr.ee/cbuchele](https://linktr.ee/cbuchele?utm_source=linktree_admin_share)

---

## 🔗 Part of the Aegis Family

- [`aegis-vault`](https://pypi.org/project/aegis-vault): Secure prompt middleware for LLMs  
- `aegis-inspect` *(coming soon)*: LLM privacy scanner & redactor audit tool  
- `aegis-agent` *(coming soon)*: Secure AI routing, jailbreaking detection, and red teaming agent

---

## 📄 License

[Apache 2.0](./LICENSE)

---

⭐️ Feel free to star this repo and contribute!

#AI #Cybersecurity #Python #LLM #DataPrivacy #OpenSource #LGPD #AegisVault #AegisAI
