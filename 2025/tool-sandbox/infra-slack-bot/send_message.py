import requests
import os
from dotenv import load_dotenv

load_dotenv()

TEST_WEBHOOK_URL = os.getenv("TEST_WEBHOOK_URL")

def send_message(text):
    payload = {"text": text}
    response = requests.post(TEST_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error sending message: {response.text}")
    else:
        print("Message sent!")

if __name__ == "__main__":
    send_message("Hello, this is a test message! :lock:")