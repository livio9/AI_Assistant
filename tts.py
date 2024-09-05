import requests
import os
from uuid import uuid4

def text2audio(content: str):
    # 假设的API URL和API KEY
    API_URL = "http://localhost:8080/tts"
    headers = {"Content-Type": "application/json"}
    data = {
        "input": content,
        "model": "en-us-blizzard_lessac-medium.onnx"
    }

    try:
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            file_path = "output.wav"
            with open(file_path, 'wb') as audio_file:
                audio_file.write(response.content)
            return file_path
        else:
            print("Error: Unable to generate audio.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    text2audio("Sun Wukong (also known as the Great Sage of Qi Tian, Sun Xing Shi, and Dou Sheng Fu) is one of the main characters in the classical Chinese novel Journey to the West")