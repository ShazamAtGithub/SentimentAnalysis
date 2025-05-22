import requests
import os

# --- Configuration ---

# Base URL of FastAPI
BASE_API_URL = "http://127.0.0.1:8000"
# Endpoint
UPLOAD_ENDPOINT = "/analyze_comments"
# Full API URL
api_url = BASE_API_URL + UPLOAD_ENDPOINT

# Path to the Excel file for testing
FILE_TO_UPLOAD_PATH = "/home/neeraj/Documents/data/instagram-comments682319a8e54ac-DJIZDwgS3yh.xlsx" # Update this path

# Check if file exists
if not os.path.exists(FILE_TO_UPLOAD_PATH):
    print(f"Error: File not found at '{FILE_TO_UPLOAD_PATH}'")
    exit()

# Send Request
try:
    # Open file in binary read mode
    with open(FILE_TO_UPLOAD_PATH, "rb") as f:
        files = {'excel_file': (os.path.basename(FILE_TO_UPLOAD_PATH), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}

        print(f"Uploading '{os.path.basename(FILE_TO_UPLOAD_PATH)}' to {api_url}...")

        # Make the POST request
        response = requests.post(api_url, files=files)

    # Response
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print("Upload successful!")
        try:
            print("Response:", response.json())
        except requests.exceptions.JSONDecodeError:
            print("Response text:", response.text)
    else:
        print("Upload failed.")
        try:
            print("Error details:", response.json())
        except requests.exceptions.JSONDecodeError:
            print("Error response text:", response.text)

except requests.exceptions.ConnectionError:
    print(f"Error: Could not connect to {BASE_API_URL}. Is the API running?")
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

