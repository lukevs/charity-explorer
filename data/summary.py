import wikipediaapi
import requests
from bs4 import BeautifulSoup as bs


def get_description(url):
        res = requests.get(url)
        soup = bs(res.text, 'html.parser')
        body = []
        for item in soup.find_all("p"):
                if item.text.startswith("The history"):
                        break
                body.append(item.text)
        return ' '.join(body)

url = 'https://en.wikipedia.org//wiki/The_Alliance_for_Safe_Children'
url = 'https://en.wikipedia.org//wiki/American_Heart_Association'
desc = get_description(url)
print(desc)

"""
wiki_wiki = wikipediaapi.Wikipedia('en')
url = 'Foundation_(nonprofit)'
page = wiki_wiki.page(url)
print(page)
"""
