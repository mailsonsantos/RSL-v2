import requests
import os
import uuid

api_key = 'sk-9Ztn4olhSGsNIduf151nRCJ8Pkcn5jrTMdRRb4wl-rM'
url = "http://localhost:7860/api/v1/run/cab4734e-9d31-4c61-89f9-3315a939185a"  # The complete API endpoint URL for this flow

# Request payload configuration
payload = {
    "output_type": "text",
    "input_type": "text",
    "input_value": "hello world!"
}
payload["session_id"] = str(uuid.uuid4())

headers = {"x-api-key": api_key}

try:
    # Send API request
    response = requests.request("POST", url, json=payload, headers=headers)
    response.raise_for_status()  # Raise exception for bad status codes

    # Print response
    print(response.text)

except requests.exceptions.RequestException as e:
    print(f"Error making API request: {e}")
except ValueError as e:
    print(f"Error parsing response: {e}")