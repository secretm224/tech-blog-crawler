import requests
from bs4 import BeautifulSoup

print("=== 올리브영 RSS 확인 ===")
urls = [
    'https://oliveyoung.tech/feed/',
    'https://oliveyoung.tech/rss/',
    'https://oliveyoung.tech/rss.xml',
    'https://oliveyoung.tech/feed.xml',
    'https://oliveyoung.tech/atom.xml',
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for url in urls:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ {url} - 성공!")
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item') or soup.find_all('entry')
            print(f"   글 개수: {len(items)}")
            if items:
                title = items[0].find('title').get_text()
                print(f"   첫 번째 글: {title[:50]}")
            break
        else:
            print(f"❌ {url} - {response.status_code}")
    except Exception as e:
        print(f"❌ {url} - 실패")