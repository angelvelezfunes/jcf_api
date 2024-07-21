import requests

# Define the URL of your FastAPI endpoint
url = 'https://api.jcfmaintenance.com:8000/send-email-reminder'

try:
    response = requests.post(url)
    response.raise_for_status()
    print(f"Success: {response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
