import speech_recognition as sr
import requests
import json
import time
import sys  # Import sys for handling keyboard interrupt
import uuid  # Import uuid for generating unique identifiers
import os  # Import os for file and directory operations
from pydub import AudioSegment  # Import AudioSegment from pydub for audio file operations
import pyaudio  # Import pyaudio for playing audio files

# Custom API endpoint
API_ENDPOINT = "http://gpt-proxy.motoemotovps.serv00.net/chat"
SYSTEM_PROMPT = ""

# Deepgram API setup
DEEPGRAM_API_KEY = ""
DEEPGRAM_API_URL = "https://api.deepgram.com/v1/speak?model=aura-zeus-en"  # Updated model name to zeus
DEEPGRAM_HEADERS = {
    "Authorization": f"Token {DEEPGRAM_API_KEY}",
    "Content-Type": "application/json"
}

# Directory for storing audio files
AUDIO_FILES_DIR = "audio_responses"
if not os.path.exists(AUDIO_FILES_DIR):
    os.makedirs(AUDIO_FILES_DIR)

def generate_response(prompt):
    request_data = {
        "message": prompt,
        "systemPrompt": SYSTEM_PROMPT
    }
    try:
        response = requests.post(API_ENDPOINT, json=request_data)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        response_data = response.json()
        return response_data.get("response")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return ""

def speak_text(text):
    # Split text into chunks of 1999 characters
    chunks = [text[i:i+1999] for i in range(0, len(text), 1999)]
    audio_files = []
    for chunk in chunks:
        payload = {"text": chunk}
        response = requests.post(DEEPGRAM_API_URL, headers=DEEPGRAM_HEADERS, json=payload)
        if response.status_code == 200:
            unique_id = str(uuid.uuid4())
            audio_file_path = os.path.join(AUDIO_FILES_DIR, f"{unique_id}.mp3")
            with open(audio_file_path, "wb") as f:
                f.write(response.content)
            audio_files.append(audio_file_path)
            print("Audio file saved successfully.")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return
    # Merge audio files if more than one
    if len(audio_files) > 1:
        merged_audio_file_path = merge_audio_files(audio_files)
        # Play merged audio file
        play_audio_file(merged_audio_file_path)
    elif audio_files:
        # Play the single audio file
        play_audio_file(audio_files[0])
    # After playing the audio, prompt to say 'Hey AI' to start recording the question
    print("Say 'Hey AI' to start recording your question...")

def play_audio_file(audio_file_path):
    # Use pyaudio to play the audio file
    try:
        audio = AudioSegment.from_file(audio_file_path)
        playback = pyaudio.PyAudio()
        stream = playback.open(format=playback.get_format_from_width(audio.sample_width),
                               channels=audio.channels,
                               rate=audio.frame_rate,
                               output=True)
        stream.write(audio.raw_data)
        stream.stop_stream()
        stream.close()
        playback.terminate()
        print(f"Finished playing audio file: {audio_file_path}")
    except Exception as e:
        print(f"Failed to play audio file: {e}")

def merge_audio_files(audio_files):
    combined = AudioSegment.empty()
    for audio_file in audio_files:
        sound = AudioSegment.from_mp3(audio_file)
        combined += sound
    merged_audio_file_path = os.path.join(AUDIO_FILES_DIR, f"{str(uuid.uuid4())}_merged.mp3")
    combined.export(merged_audio_file_path, format="mp3")
    print(f"Audio files merged successfully: {merged_audio_file_path}")
    return merged_audio_file_path

# Removed listen_for_user function as it's no longer directly called after playing audio

def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
    return ""

def main():
    try:  # Wrap the main loop in a try block to catch KeyboardInterrupt
        while True:
            print("Wait for user to say 'Hey AI'")
            print("Say 'Hey AI' to start recording your question...")
            with sr.Microphone() as source:
                recognizer = sr.Recognizer()
                audio = recognizer.listen(source)
                try:
                    transcription = recognizer.recognize_google(audio)
                    if transcription.lower() == "hey ai":
                        print("Say your question...")
                        filename = "input.wav"
                        with sr.Microphone() as source:
                            recognizer = sr.Recognizer()
                            audio = recognizer.listen(source)
                            with open(filename, "wb") as f:
                                f.write(audio.get_wav_data())
                        text = transcribe_audio_to_text(filename)
                        if text:
                            print(f"You said: {text}")
                            response = generate_response(text)
                            print("Custom GPT-3 says: ", response)
                            speak_text(response)
                except Exception as e:
                    print(f"An error occurred: {e}")
    except KeyboardInterrupt:  # Catch the KeyboardInterrupt exception
        print("\nProgram exited by user.")
        sys.exit()  # Exit the program

if __name__ == "__main__":
    main()

