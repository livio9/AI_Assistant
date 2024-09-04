import os
import json
import requests

def image_generate(content: str):
    # print(content)
    # 定义请求header格式位JSON
    headers = {"Content-Type": "application/json"}

    # 设置data参数：content为图像描述，size为图像大小
    data = json.dumps({"prompt": content, "size": "256x256"})

    # 发送请求到本地服务器图像生成端点
    response = requests.post("http://localhost:8080/v1/images/generations", headers=headers, data=data)

    print(response.status_code)
    # 如果http成功相应，返回图像的url
    if response.status_code == 200:
        # print(response.json().get("data")[0].get("url"))
        return response.json().get("data")[0].get("url")
    else:
        print("error")
        return None
if __name__ == "__main__":
    image_generate('A cute baby sea otter')