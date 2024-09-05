import requests

def audio2text(file):
    url = "http://localhost:8080/v1/audio/transcriptions"

    files = {
        'file': (file.replace("\\", "/"), open(file, 'rb')),
        'model': (None, 'whisper-1')
    }

    try:
        response = requests.post(url, files=files)
        # 检查响应状态码
        if response.status_code == 200:
            result = response.json()
            # 获取转录的文本
            segments = result.get("segments", [])
            transcribed_text = " ".join(segment["text"] for segment in segments)
            return transcribed_text
        else:
            print("Error: Unable to transcribe audio.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    print(audio2text('sun-wukong.wav'))