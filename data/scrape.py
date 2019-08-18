from bs4 import BeautifulSoup as bs
import requests
import csv

BASE_URL = 'https://en.wikipedia.org'
CHARITY_URL = 'https://en.wikipedia.org/wiki/List_of_charitable_foundations'

def get_description(url):
        res = requests.get(url)
        soup = bs(res.text, 'html.parser')
        body = []
        for item in soup.find_all("p"):
                if item.text.startswith("The history"):
                        break
                body.append(item.text)
        return ' '.join(body)

res = requests.get(CHARITY_URL)
soup = bs(res.text, "html.parser")
charities = {}
content = soup.find('div', {'id': 'content'})
for link in content.find_all("a"):
    url = link.get("href", "")
    if "/wiki" in url and url.count('/') == 2 and ':' not in url:
        charities[link.text.strip()] = "%s%s" % (BASE_URL, url)

with open('charities.csv', 'w') as f:
    csv_file = csv.writer(f, delimiter='\t')
    names = list(charities.keys())
    print('found', len(names))
    for i, charity_name in enumerate(names):
        url = charities[charity_name]
        description = get_description(url)
        row = [charity_name, url, description]
        print('row', row)
        csv_file.writerow(row)

f.close()

