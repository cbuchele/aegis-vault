"""
Basic usage example of Aegis Vault with system prompts.
"""
from aegis_vault import VaultGPT

def main():
    # Initialize the vault with a custom system prompt
    vault = VaultGPT(
        encryption_key="test-key-123",
        system_prompt="""
        You are a helpful assistant that processes text with sensitive information.
        
        IMPORTANT: The user's message may contain special markers like <<VAULT_0>>, <<VAULT_1>>, etc.
        These markers represent redacted sensitive information.
        
        RULES:
        1. NEVER modify, remove, or reorder these markers in your response
        2. Return all markers exactly as they appear in the input
        3. If you need to refer to the redacted content, use the marker itself
        4. Do not try to guess what the markers represent
        """.strip()
    )
    
    # Example function that simulates an LLM call
    def mock_llm(prompt: str, **kwargs) -> str:
        print("\n--- LLM Received ---")
        print(f"System prompt: {kwargs.get('system_prompt', 'None')}")
        print(f"User prompt: {prompt}")
        
        # Simulate an LLM that might try to modify the markers
        response = """
        I've processed your request. The redacted information (<<VAULT_0>> and <<VAULT_1>>) 
        has been securely handled. I see you mentioned <<VAULT_0>> specifically.
        """.strip()
        
        print("\n--- LLM Responding ---")
        print(f"Response with preserved markers: {response}")
        return response
    
    # Example with sensitive information
    sensitive_text = """
    Customer Information:
    - Name: Maria Silva
    - Email: maria.silva@example.com
    - CPF: 987.654.321-00
    - Phone: +55 11 98765-4321
    """
    
    print("=== Original Text ===")
    print(sensitive_text)
    
    # Process the text through the vault
    print("\n=== Processing with Aegis Vault ===")
    result = vault.secure_chat(sensitive_text, mock_llm)
    
    print("\n=== Final Result ===")
    print(f"Original text: {sensitive_text}")
    print(f"Processed text: {result}")
    
    # Show the vault contents
    print("\n=== Vault Contents ===")
    for idx, entry in vault.vault.items():
        print(f"{idx}: {entry['type']} = {entry['original']}")

if __name__ == "__main__":
    main()
