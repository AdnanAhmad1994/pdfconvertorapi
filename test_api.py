import requests
import os
import time
import json
from pathlib import Path

def test_api():
    """
    Test the PDF Converter API by converting a test PDF to DOCX and JPEG.
    """
    # API endpoints
    BASE_URL = "http://localhost:8000"
    CONVERT_ENDPOINT = f"{BASE_URL}/api/v1/conversion/"
    STATUS_ENDPOINT = f"{BASE_URL}/api/v1/conversion/"
    DOWNLOAD_ENDPOINT = f"{BASE_URL}/api/v1/conversion/"
    HEALTH_ENDPOINT = f"{BASE_URL}/health"
    
    # Test file
    TEST_PDF_PATH = "C:/Xesium/pdfconvertorapi/tmp/test.pdf"
    
    print("=== PDF Converter API Test ===")
    
    # Step 1: Check if API is running
    try:
        print("\nChecking if API is running...")
        response = requests.get(HEALTH_ENDPOINT)
        
        if response.status_code == 200:
            print(f"API is running: {response.json()}")
        else:
            print(f"Error: API returned status code {response.status_code}")
            return
    except Exception as e:
        print(f"Error connecting to API: {str(e)}")
        print("Make sure the API is running with 'python -m uvicorn app.main:app --reload'")
        return
    
    # Step 2: Convert PDF to DOCX
    try:
        print("\nTesting PDF to DOCX conversion...")
        
        # Prepare the file and form data
        with open(TEST_PDF_PATH, "rb") as f:
            files = {"file": (os.path.basename(TEST_PDF_PATH), f, "application/pdf")}
            data = {"format": "docx", "preserve_layout": "true"}
            
            # Send the conversion request
            response = requests.post(CONVERT_ENDPOINT, files=files, data=data)
            
            if response.status_code == 200:
                task_data = response.json()
                task_id = task_data["task_id"]
                print(f"Conversion started: Task ID {task_id}")
                
                # Check status until completed or failed
                while True:
                    status_response = requests.get(f"{STATUS_ENDPOINT}{task_id}")
                    status_data = status_response.json()
                    print(f"Status: {status_data['status']} - Progress: {status_data['progress']}%")
                    
                    if status_data["status"] in ["completed", "failed"]:
                        if status_data["status"] == "completed":
                            # Download the converted file
                            download_url = f"{DOWNLOAD_ENDPOINT}{task_id}/download"
                            download_response = requests.get(download_url)
                            
                            if download_response.status_code == 200:
                                # Save the downloaded file
                                output_path = "C:/Xesium/pdfconvertorapi/tmp/test_docx_output.docx"
                                with open(output_path, "wb") as out_file:
                                    out_file.write(download_response.content)
                                print(f"Downloaded DOCX file to: {output_path}")
                            else:
                                print(f"Error downloading file: {download_response.status_code}")
                        else:
                            print(f"Conversion failed: {status_data.get('message', 'Unknown error')}")
                        break
                    
                    time.sleep(2)  # Wait before checking again
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"Error in DOCX conversion test: {str(e)}")
    
    # Step 3: Convert PDF to JPEG
    try:
        print("\nTesting PDF to JPEG conversion...")
        
        # Prepare the file and form data
        with open(TEST_PDF_PATH, "rb") as f:
            files = {"file": (os.path.basename(TEST_PDF_PATH), f, "application/pdf")}
            data = {"format": "jpeg", "quality": "90", "dpi": "300"}
            
            # Send the conversion request
            response = requests.post(CONVERT_ENDPOINT, files=files, data=data)
            
            if response.status_code == 200:
                task_data = response.json()
                task_id = task_data["task_id"]
                print(f"Conversion started: Task ID {task_id}")
                
                # Check status until completed or failed
                while True:
                    status_response = requests.get(f"{STATUS_ENDPOINT}{task_id}")
                    status_data = status_response.json()
                    print(f"Status: {status_data['status']} - Progress: {status_data['progress']}%")
                    
                    if status_data["status"] in ["completed", "failed"]:
                        if status_data["status"] == "completed":
                            # Download the converted file
                            download_url = f"{DOWNLOAD_ENDPOINT}{task_id}/download"
                            download_response = requests.get(download_url)
                            
                            if download_response.status_code == 200:
                                # Save the downloaded file
                                output_path = "C:/Xesium/pdfconvertorapi/tmp/test_jpeg_output.zip"  # For multiple pages
                                with open(output_path, "wb") as out_file:
                                    out_file.write(download_response.content)
                                print(f"Downloaded JPEG file to: {output_path}")
                            else:
                                print(f"Error downloading file: {download_response.status_code}")
                        else:
                            print(f"Conversion failed: {status_data.get('message', 'Unknown error')}")
                        break
                    
                    time.sleep(2)  # Wait before checking again
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"Error in JPEG conversion test: {str(e)}")
    
    print("\n=== Test Completed ===")

if __name__ == "__main__":
    test_api()
