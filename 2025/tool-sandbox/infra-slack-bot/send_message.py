import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TEST_WEBHOOK_URL = os.getenv("TEST_WEBHOOK_URL")

members = ["Alice", "Bob", "Charlie", "David"]
STATE_FILE = "state.json"

def send_message(text):
    payload = {"text": text}
    response = requests.post(TEST_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error sending message: {response.text}")
    else:
        print("Message sent!")

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"index": 0}
    
def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def is_holiday():
    today = datetime.today().strftime("%Y-%m-%d")
    year = datetime.today().year
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/JP"
    res = requests.get(url)

    if res.status_code != 200:
        print(f"Error fetching holidays: {res.status_code}")
        return False

    holidays = res.json()
    for holiday in holidays:
        if holiday["date"] == today:
            return True
    return False

def rotate_and_notify():
    if is_holiday():
        send_message("今日は祝日なので担当者はいません！")
        return
    
    state = load_state()
    index = state["index"] % len(members)
    today_member = members[index]

    send_message(f"今日の担当者は {today_member} さんです！")

    state["index"] = index + 1
    save_state(state)

if __name__ == "__main__":
    rotate_and_notify()