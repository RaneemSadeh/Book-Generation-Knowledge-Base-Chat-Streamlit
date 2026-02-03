import requests
import json
import sys

URL = "http://127.0.0.1:8000/chat/"

def test_chat():
    prompt = "What are the 9 training methods mentioned in the text?"
    
    print(f"Sending prompt: {prompt}")
    
    try:
        response = requests.post(URL, json={"prompt": prompt})
        
        if response.status_code == 200:
            print("\nSuccess!")
            data = response.json()
            print("Response from Gemini:")
            print("-" * 40)
            print(data["response"])
            print("-" * 40)
        else:
            print(f"\nFailed with status code: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server. Is it running?")
        print("Run 'python -m app.main' in a separate terminal.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
       # Allow custom prompt from CLI
       # BUT user just wants a verifier, so defaulting is fine.
       pass
    test_chat()
