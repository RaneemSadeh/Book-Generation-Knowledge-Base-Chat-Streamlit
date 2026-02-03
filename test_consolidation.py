import requests
import os

url = "http://localhost:8000/consolidate/"

print("Requesting consolidation...")
try:
    response = requests.post(url, timeout=300) # Long timeout for GenAI
    
    if response.status_code == 200:
        print("Success!")
        data = response.json()
        print(f"Message: {data.get('message')}")
        print(f"File saved at: {data.get('file')}")
        print("Preview:")
        print(data.get('content_preview'))
    else:
        print(f"Failed with status {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
