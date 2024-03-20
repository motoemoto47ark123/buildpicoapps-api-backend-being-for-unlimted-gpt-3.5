import requests
import json
import sys

API_ENDPOINT = "https://qz83c6-8000.csb.app/chat"

SYSTEM_PROMPT = "You are a good AI assistant. You will only tell me how nice I talk to you."

def send_request(message, chat_id=None):
    request_data = {
        "chatId": chat_id,
        "message": message,
        "systemPrompt": SYSTEM_PROMPT
    }

    try:
        response = requests.post(API_ENDPOINT, json=request_data)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        response_data = response.json()
        # Filter the response to only show the text part
        if 'response' in response_data:
            print(response_data['response'])
        else:
            print("Response from AI not found.")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def main():
    chat_id = "123e4567-e89b-12d3-a456-426655440003"
    while True:
        user_message = input("You: ")
        if user_message.lower() == "esc":
            print("Exiting chat...")
            break
        send_request(user_message, chat_id)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram exited by user.")
        sys.exit()
