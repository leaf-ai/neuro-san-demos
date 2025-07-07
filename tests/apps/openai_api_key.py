import os

from neuro_san.internals.run_context.langchain.util.api_key_error_check import ApiKeyErrorCheck
from openai import OpenAI


# Method for Testing OpenAI API key
#  Reads the OpenAI API key from an environment variable,
#  Creates a client, and submits a simple query ("What's the capital of France?").
#  The response should includes the word "Paris".
#  Any exceptions (Invalid API Key, OpenAI access being blocked, etc.) are reported.
def test_open_ai_api_key():

    # Set up the client with your API key
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = None
    try:

        # Make a chat completion request
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What's the capital of France?"},
            ],
        )

        # Print the assistant's reply
        print("Successful call to OpenAI")
        print(f"reponse: {response.choices[0].message.content}")

    except Exception as e:
        print("Failed call to OpenAI")
        exception_msg = ApiKeyErrorCheck.check_for_api_key_exception(e)
        print(f"Exception message: {exception_msg}")


if __name__ == "__main__":
    test_open_ai_api_key()
