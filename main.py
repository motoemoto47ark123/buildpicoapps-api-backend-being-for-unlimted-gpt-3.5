import asyncio
import json
import websockets

# Define a function to generate a story based on a given topic


async def generate_story(topic):
    # WebSocket URI to connect to the backend service
    uri = "wss://backend.buildpicoapps.com/ask_ai_streaming_v2"

    # Connect to the WebSocket server
    async with websockets.connect(uri) as websocket:
        # Prepare the prompt message with the topic
        prompt = f"Generate a story based on the topic: {topic}"

        # Send the prompt message to the WebSocket server
        await websocket.send(json.dumps({
            "appId": "also-really",
            "prompt": prompt
        }))

        # Receive and accumulate story output from the server
        output = ''
        async for message in websocket:
            output += message

        # Return the generated story
        return output


async def main():
    # Read the topic from the file "code.txt"
    with open("code.txt", "r") as file:
        topic = file.read()

    # Generate a story based on the topic and retrieve the result
    result = await generate_story(topic)

    # Print the generated story to the console
    print("Generated story:")
    print(result)

    # Write the generated story to the file "output.txt", overwriting existing content
    with open("output.txt", "w") as file:
        file.write(result)

# Entry point of the program
if __name__ == "__main__":
    # Run the main coroutine
    asyncio.run(main())
