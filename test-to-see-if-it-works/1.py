import requests
import json
import sys

API_ENDPOINT = "https://qz83c6-8000.csb.app/chat"

SYSTEM_PROMPT = "You are a good AI assistant. You will only tell me how nice I talk to you."

# Initialize chatId as None to check if it's the first request
chatId = None

def send_request(message):
    global chatId
    request_data = {
        "message": message,
        "systemPrompt": SYSTEM_PROMPT
    }
    # If chatId exists, add it to the request data
    if chatId:
        request_data["chatId"] = chatId

    try:
        response = requests.post(API_ENDPOINT, json=request_data)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        response_data = response.json()
        # Update chatId from the response for subsequent requests
        chatId = response_data.get("chatId")
        # Print only the text from the AI in the response
        print(response_data.get("response"))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def main():
    while True:
        user_message = input("You: ")
        if user_message.lower() == "esc":
            print("Exiting chat...")
            break
        send_request(user_message)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram exited by user.")
        sys.exit()

