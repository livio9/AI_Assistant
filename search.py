import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

def search(content: str):
    search = GoogleSearch({
        "q": content,
        "engine": "bing",
        "api_key": "05c25def8c46399d93f8b860fc8628d16d5279160256e33f3eabca9f5b3f87b3"
    })
    results = search.get_dict()
    for result in results["organic_results"]:
        if "snippet" in result:
            snippet = result["snippet"]
            return f"Please answer {content} based on the search result: {snippet}"
        else:
            return ""

if __name__ == "__main__":
    search("Sun Wukong")