"""
Example integration of Aegis Vault with various LLM providers.

This example shows how to use Aegis Vault with different LLM providers
while ensuring vault markers are preserved in the responses.
"""
from typing import Dict, List, Any, Optional, Union
from aegis_vault import VaultGPT

# Initialize the vault with a custom system prompt
vault = VaultGPT(
    encryption_key="my-secure-key-123",
    system_prompt="""
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
)

def openai_chat_completion(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Example function showing how to use with OpenAI's ChatCompletion API.
    
    In a real implementation, you would make an actual API call to OpenAI.
    This is a simplified example that simulates the behavior.
    """
    print(f"\n--- OpenAI Chat Completion ---")
    print(f"System prompt: {vault.get_system_prompt()}")
    print(f"User prompt: {prompt}")
    
    # In a real implementation, this would be an actual API call:
    # response = openai.ChatCompletion.create(
    #     model=model,
    #     messages=[
    #         {"role": "system", "content": vault.get_system_prompt()},
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    # return response.choices[0].message['content']
    
    # Simulated response that preserves vault markers
    return f"I noticed you mentioned <<VAULT_0>> and <<VAULT_1>>. These have been securely redacted."

def anthropic_completion(prompt: str, model: str = "claude-2") -> str:
    """
    Example function showing how to use with Anthropic's API.
    """
    print(f"\n--- Anthropic Completion ---")
    print(f"System prompt: {vault.get_system_prompt()}")
    print(f"User prompt: {prompt}")
    
    # Simulated response that preserves vault markers
    return f"I'll help process your request. I see you mentioned <<VAULT_0>> and <<VAULT_1>>."

def custom_llm_provider(prompt: str, **kwargs) -> str:
    """
    Example of a custom LLM provider function that accepts a system prompt.
    """
    system_prompt = kwargs.get('system_prompt', '')
    print(f"\n--- Custom LLM Provider ---")
    print(f"System prompt: {system_prompt}")
    print(f"User prompt: {prompt}")
    
    # Simulated response that preserves vault markers
    return f"Processing your request. I'll keep <<VAULT_0>> and <<VAULT_1>> intact."

def main():
    # Example prompt with sensitive information
    sensitive_prompt = """
    Please analyze this customer information:
    - Name: John Doe
    - Email: john.doe@example.com
    - CPF: 123.456.789-00
    - Address: 123 Main St, Anytown, 12345
    
    They reported an issue with order #12345.
    """
    
    # Example 1: Using with OpenAI's API
    print("=== Example 1: OpenAI Chat Completion ===")
    response = vault.secure_chat(
        sensitive_prompt,
        openai_chat_completion,
        model="gpt-4"  # Passed as kwargs to the llm_function
    )
    print(f"Final response with restored data: {response}")
    
    # Example 2: Using with Anthropic's API
    print("\n=== Example 2: Anthropic Completion ===")
    response = vault.secure_chat(
        sensitive_prompt,
        anthropic_completion,
        model="claude-2"
    )
    print(f"Final response with restored data: {response}")
    
    # Example 3: Using with a custom LLM provider
    print("\n=== Example 3: Custom LLM Provider ===")
    response = vault.secure_chat(
        sensitive_prompt,
        custom_llm_provider,
        custom_param="value"  # Additional custom parameters
    )
    print(f"Final response with restored data: {response}")
    
    # Example 4: Manual system prompt handling
    print("\n=== Example 4: Manual System Prompt ===")
    # Get the system prompt manually
    system_prompt = vault.get_system_prompt()
    # Pass it to your LLM function as needed
    print(f"System prompt to use: {system_prompt[:100]}...")

if __name__ == "__main__":
    main()
