import os

from neuro_san.internals.run_context.langchain.util.api_key_error_check import ApiKeyErrorCheck
import google.generativeai as genai


# Method for Testing Gemini API key
#  Reads the Gemini API key from an environment variable,
#  Creates a client, and submits a simple query ("What's the capital of France?").
#  The response should includes the word "Paris".
#  Any exceptions (Invalid API Key, provider access being blocked, etc.) are reported.
def test_gemini_api_key():

    # Set your Gemini details
    api_key = os.getenv("GOOGLE_API_KEY")  # or use a string directly
    model_name = os.getenv("GOOGLE_MODEL_NAME")  # e.g., "gemini-2.5-pro"

    try:

        # Load your Gemini API key
        genai.configure(api_key=api_key, transport='rest')  # Or just use: "your-key-here"

        # Create a Gemini model client
        model = genai.GenerativeModel(model_name)

        # Send a simple prompt
        response = model.generate_content("What's the capital of France?")

        print("Successful call to Gemini")
        print(response.text)

    except Exception as e:
        print("Failed call to Gemini")
        exception_msg = ApiKeyErrorCheck.check_for_api_key_exception(e)
        print(f"Exception message: {exception_msg}")


if __name__ == "__main__":
    test_gemini_api_key()
