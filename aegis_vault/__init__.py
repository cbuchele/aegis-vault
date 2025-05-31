"""
Aegis Vault - Secure, LGPD-compliant middleware for LLM prompt protection.

This package provides tools for detecting, redacting, and encrypting
sensitive data in prompts before sending them to LLMs.
"""

from .middleware import VaultGPT

__version__ = "0.1.0"
__author__ = "Your Name <your.email@example.com>"
__all__ = ["VaultGPT", "__version__"]
