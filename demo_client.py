import requests

BASE_URL = "http://localhost:8000/conversational/query"

# This will hold the session_id for the entire conversation
session_id = None

def send_message(message: str):
    global session_id
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id  # reuse existing session

    response = requests.post(BASE_URL, json=payload)
    data = response.json()

    # Update session_id from the first response
    if not session_id:
        session_id = data.get("session_id")

    return data

if __name__ == "__main__":
    print("=== Chat Demo ===")
    while True:
        user_msg = input("You: ")
        if user_msg.lower() in ["exit", "quit"]:
            print("Ending chat.")
            break

        res = send_message(user_msg)
        print("AI:", res.get("answer"))