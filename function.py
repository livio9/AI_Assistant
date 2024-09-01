import os
import requests
from typing import List, Dict
import openai
import json

# 设置API密钥为任意非空字符串
openai.api_key = "any_non_empty_string"

# 设置本地 API 基础路径
openai.api_base = "http://localhost:8080/v1"

weather_key = "3299ad4c61fe4277b4d8ea793f066bb4"

todo_list = []

def lookup_location_id(location: str):
    """
    TODO
    """
    reback = requests.get(f"https://geoapi.qweather.com/v2/city/lookup?location={location}&key={weather_key}")
    return reback.json().get('location')[0].get('id')

def get_current_weather(location: str):
    """
    TODO
    """
    id = lookup_location_id(location)
    reback = requests.get(f"https://devapi.qweather.com/v7/weather/now?location={id}&key={weather_key}")
    temp = reback.json().get('now').get('temp')
    text = reback.json().get('now').get('text')
    humidity = reback.json().get('now').get('humidity')
    
    return f"Temperature: {temp} Description:{text} Humidity: {humidity}"

def add_todo(todo: str):
    """
    TODO
    """
    todo_list.append(todo)
    reback = ""
    for i in range(len(todo_list)):
        reback += f"• {todo_list[i]}\n"
    return reback

def function_calling(messages: List[Dict]):
    """
    TODO
    """
    functions = [
    {
        "name": "get_current_weather",
        "description": "Return the temperature of the specified region specified by the user",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "User specified region",
                },
                "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "temperature unit"
                    },
            },
            "required": ["location"],
        },
    },
    {
        "name": "add_todo",
        "description": "Add a todo thing to the todo list",
        "parameters": {
            "type": "object",
            "properties": {
                "todo": {
                    "type": "string", 
                    "description": "The todo thing to be added to the todo list",
                },
            },
            "required": ["todo"],
        },
    },
]
    response = openai.ChatCompletion.create(
        model="ggml-openllama.bin",
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    func = response.choices[0].message.function_call["name"]
    params = json.loads(response.choices[0].message.function_call["arguments"])
    if(func == "get_current_weather"):
        return get_current_weather(params["location"])
    elif(func == "add_todo"):
        return add_todo(params["todo"])
    else:
        return "Function not found"


if __name__ == "__main__":
    messages = [{"role": "user", "content": "What's the weather like in Beijing?"}]
    response = function_calling(messages)
    print(response)

    messages = [{"role": "user", "content": "Add a todo: walk"}]
    response = function_calling(messages)
    print(response)