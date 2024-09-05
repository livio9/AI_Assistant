import requests
from bs4 import BeautifulSoup

def fetch(url: str):
    # 发送HTTP请求获取网页内容
    response = requests.get(url)
    # 确保请求成功
    if response.status_code == 200:
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找所有的<p>标签
        p_tags = soup.find_all('p')
        # 提取所有<p>标签的文本内容
        content = ' '.join([tag.get_text() for tag in p_tags if tag.get_text().strip() != ''])
        return content
    else:
        return f"Failed to fetch content. Status code: {response.status_code}"

if __name__ == "__main__":
    fetch("https://dev.qweather.com/en/help")
