import os

import anthropic
from neuro_san.internals.run_context.langchain.util.api_key_error_check import ApiKeyErrorCheck


# Method for Testing Anthropic API key
#  Reads the Anthropic API keys from an environment variables,
#  Creates a client, and submits a simple query ("What's the capital of France?").
#  The response should includes the word "Paris".
#  Any exceptions (Invalid API Key, provider access being blocked, etc.) are reported.
def test_anthropic_api_key():

    # Set your Anthropic details
    api_key = os.getenv("ANTHROPIC_API_KEY")  # or use a string directly

    # Set model to the model you want to use, e.g., "claude-opus-4-20250514"
    model = "claude-opus-4-20250514"

    # Create Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Set up the client with your API key
    try:
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": [{"type": "text", "text": "What's the capital of France?"}]}],
        )

        # Print the assistant's reply
        print("Successful call to Anthropic")
        print(f"reponse: {message.content[0].text}")

    except Exception as e:
        print("Failed call to Anthropic")
        print(f"Exception: {e}")
        exception_msg = ApiKeyErrorCheck.check_for_api_key_exception(e)
        print(f"Exception message: {exception_msg}")


if __name__ == "__main__":
    test_anthropic_api_key()
