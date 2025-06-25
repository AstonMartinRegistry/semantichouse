import os
import requests
from dotenv import load_dotenv
import json
import subprocess
import time

load_dotenv()

# Get the OpenAI API key from environment variables
api_key = os.getenv("OPEN_AI_KEY")
if not api_key:
    raise ValueError("OPEN_AI_KEY environment variable is not set.")

def upload_to_0x0(file_path):
    try:
        result = subprocess.run([
            'curl', '-F', f'file=@{file_path}', 'https://file.io'
        ], capture_output=True, text=True)
        if result.returncode == 0:
            url = result.stdout.strip()
            if url.startswith('https://'):
                return url
            else:
                print(f"Unexpected response from file.io: {url}")
                return None
        else:
            print(f"curl failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error uploading file with curl: {e}")
        return None

def get_information(image_url):
    print(f"\nDebug: Image URL being used: {image_url}")
    print(f"Debug: Testing image URL accessibility...")
    try:
        response = requests.head(image_url)
        print(f"Debug: Image URL response status: {response.status_code}")
        print(f"Debug: Image URL content type: {response.headers.get('content-type', 'unknown')}")
    except Exception as e:
        print(f"Debug: Error checking image URL: {str(e)}")

    prompt = """
What is the architectural style of the building?
"""

    messages = [
        {
            "role": "user",
            "content": [
                {   
                    "type": "text", 
                    "text": prompt
                },
                {
                    "type": "image_url", 
                    "image_url": {
                        "url": image_url,
                        "detail": "low"
                    }
                }
            ]
        }
    ]
    
    payload = {
        "model": "gpt-4o",
        "messages": messages,
        "max_tokens": 300  # Increased token limit for longer response
    }
    
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"Debug: API Request Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        print(f"Debug: API Response Status Code: {response.status_code}")
        print(f"Debug: API Response Body: {response.text}")
        
        if response.status_code != 200:
            return None
        
        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            response_text = response_json['choices'][0]['message']['content']
            print(f"\nFull Response:\n{response_text}")
            return response_text
    except Exception as e:
        print(f"Error during API call: {str(e)}")
    
    return None

# Get first image from building_images directory
image_dir = "building_images"
png_files = [f for f in os.listdir(image_dir) if f.endswith(".png")]
if not png_files:
    print("No PNG files found in building_images directory")
    exit(1)

first_image = png_files[18]
image_path = os.path.join(image_dir, first_image)
print(f"\n=== Processing Image: {first_image} ===")

# Use the Imgur URL directly
image_url = "https://imgur.com/a/w6HNvLF"
result = get_information(image_url)
print(f"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&Result: {result}")

# Append to or create the JSON file
json_path = "building_info_with_description.json"
existing_data = []
if os.path.exists(json_path):
    try:
        with open(json_path, "r") as f:
            existing_data = json.load(f)
            if not isinstance(existing_data, list):
                existing_data = [existing_data]
    except Exception as e:
        print(f"Warning: Could not read existing JSON file: {e}")
        existing_data = []

existing_data.append({"image": first_image, "analysis": result})
with open(json_path, "w") as f:
    json.dump(existing_data, f, indent=2)
print("\n✓ Appended result to building_info_with_description.json")



