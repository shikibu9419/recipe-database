from bs4 import BeautifulSoup
import requests

def get_title_from_url(url: str) -> str:
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup.find('title').text

def truncate(string: str, length: int, ellipsis: str = '...'):
    return f"{string[:length]}{ellipsis if string[:length] else ''}"