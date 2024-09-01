import os
import re
import openai


# 设置API密钥为任意非空字符串
openai.api_key = "any_non_empty_string"

# 设置本地 API 基础路径
openai.api_base = "http://localhost:8080/v1"

def generate_text(prompt):
    """
    TODO
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    return response

def generate_answer(current_file_text: str, content: str):
    """
    TODO
    """
    question = f"Based on {current_file_text}, Answer the questions {content} "
    return question


def generate_summary(current_file_text: str):
    """
    TODO
    """
    summary_prompt = f"Summarize the following text: \"{current_file_text}"
    return summary_prompt


if __name__ == "__main__":
    prompt = generate_answer("Hello", "Who is Sun Wukong?")
    generate_text(prompt)