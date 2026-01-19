import requests
from bs4 import BeautifulSoup

print("=== 카카오 RSS 확인 (인코딩 수정) ===")
url = 'https://tech.kakao.com/feed/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'xml')
items = soup.find_all('item')
print(f"글 개수: {len(items)}")

if items:
    print("\n=== 첫 번째 글 ===")
    title = items[0].find('title').get_text()
    link = items[0].find('link').get_text()
    print(f"제목: {title}")
    print(f"링크: {link}")