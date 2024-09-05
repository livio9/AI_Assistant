import requests
from bs4 import BeautifulSoup


def fetch(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        main_tag = soup.find('main')
        if main_tag:
            first_p = main_tag.find('p')
            if first_p:
                text = first_p.text
                content = f"Use simple words to summarize {url}. The following is the content: \n\n{text}"
                return content
            else:
                return "Wrong request"
        else:
            return "Wrong request"
    else:
        return "Wrong request"


if __name__ == "__main__":
    fetch("https://dev.qweather.com/en/help")