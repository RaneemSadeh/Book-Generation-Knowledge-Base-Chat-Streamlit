import requests
import os

url = "http://localhost:8000/extract/"
file_path = r"c:\projects\python\Ragheed\book generation Dr. Fahed pipeline\v1.0 test extraction\Files_for_testing\دورة تدريب متدربين TOT.docx"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

print(f"Sending file: {file_path}")
try:
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
        
    if response.status_code == 200:
        print("Success!")
        data = response.json()
        if "extracted_content" in data:
            content_len = len(data["extracted_content"])
            print(f"Received extracted content. Length: {content_len}")
            print("First 100 chars:", data["extracted_content"][:100])
        else:
            print("extracted_content key missing!")
            print(data.keys())
    else:
        print(f"Failed with status {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
