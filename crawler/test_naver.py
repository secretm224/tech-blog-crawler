import requests
from bs4 import BeautifulSoup

url = 'https://d2.naver.com/d2.atom'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'xml')

entries = soup.find_all('entry')
print(f"글 개수: {len(entries)}")

if entries:
    print("\n=== 첫 번째 글 구조 ===")
    print(entries[0].prettify()[:1500])