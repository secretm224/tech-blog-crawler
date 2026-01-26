import requests
from bs4 import BeautifulSoup

print("=== 야놀자 기술블로그 RSS 확인 ===")
urls = [
    'https://medium.com/feed/yanoljacloud-tech',
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for url in urls:
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            print(f"✅ {url} - 성공!")
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item')
            print(f"   글 개수: {len(items)}")
            if items:
                title = items[0].find('title').get_text()
                print(f"   첫 번째 글: {title[:50]}")
                
                # 구조 확인
                print("\n=== 첫 번째 글 구조 ===")
                print(items[0].prettify()[:1500])
        else:
            print(f"❌ {url} - {response.status_code}")
    except Exception as e:
        print(f"❌ {url} - 실패: {e}")