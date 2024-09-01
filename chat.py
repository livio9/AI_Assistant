import os
import openai

# 设置API密钥为任意非空字符串
openai.api_key = "any_non_empty_string"

# 设置本地 API 基础路径
openai.api_base = "http://localhost:8080/v1"

def chat(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=150
    )
    return response["choices"][0]["message"]["content"]