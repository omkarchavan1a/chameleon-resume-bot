import requests
import os

BASE_URL = "http://localhost:8001"

def test_extract_pdf():
    print("Testing PDF Extraction...")
    # Create a dummy tiny PDF header
    dummy_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    files = {'file': ('test.pdf', dummy_pdf, 'application/pdf')}
    try:
        response = requests.post(f"{BASE_URL}/api/extract-pdf", files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_generate_resume():
    print("\nTesting Resume Generation...")
    payload = {
        "master_data": "Software Engineer with 5 years experience in Python and FastAPI.",
        "target_position": "Senior Backend Developer",
        "target_city": "Santa Clara",
        "job_description": "We are looking for a Senior Developer with FastAPI skills.",
        "theme": "bold"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/generate-resume", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Successfully generated resume content!")
        else:
            print(f"Error details: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_extract_pdf()
    test_generate_resume()
