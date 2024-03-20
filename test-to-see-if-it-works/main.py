import asyncio
import websockets
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# URL of the wss server
WSS_URL = "wss://backend.buildpicoapps.com/api/chatbot/chat"

# Default system prompt for the chatbot
DEFAULT_SYSTEM_PROMPT = "You are the Code Maker, a friendly and professional Python programming guru tailored to assist 'Motoe' in all aspects of coding. Your focus is on providing clear and straightforward guidance and solutions, addressing 'Motoe' by name to personalize each interaction. You're equipped to handle a wide range of Python-related topics, from general programming challenges to specialized fields like data analysis and machine learning, ensuring 'Motoe's' queries are met with precise and expert advice. Stay ready to assist 'Motoe' with any Python programming need that arises."

async def send_wss_request(data):
    try:
        async with websockets.connect(WSS_URL) as wss:
            # Use the provided system prompt if available, otherwise use the default
            system_prompt = data.get("systemPrompt", DEFAULT_SYSTEM_PROMPT)

            request_data = {
                "chatId": data.get("chatId", ""),
                "appId": "happy-rest",
                "systemPrompt": system_prompt,
                "message": data.get("message", "")
            }
            await wss.send(json.dumps(request_data))

            # Initialize the response
            response = {}

            # Receive the response from the wss server as a stream
            async for message in wss:
                # Append the streamed message to the response
                response["response"] = response.get("response", "") + message

            return response
    except websockets.exceptions.ConnectionClosed as e:
        # Handle connection closed errors
        error_message = {"error": f"Connection closed: {e.code} - {e.reason}"}
        return error_message
    except Exception as e:
        # Handle other exceptions
        error_message = {"error": str(e)}
        return error_message

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        response = asyncio.run(send_wss_request(data))
        return jsonify(response)
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)