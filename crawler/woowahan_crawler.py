# crawler/woowahan_crawler.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from database import Database

class WoowahanCrawler:
    def __init__(self):
        self.blog_id = 'woowahan'
        self.base_url = 'https://techblog.woowahan.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.db = Database()
    
    def parse_date(self, date_str):
        """날짜 문자열을 datetime으로 변환 (예: Dec.26.2025)"""
        try:
            return datetime.strptime(date_str, '%b.%d.%Y')
        except:
            return None
        
    def fetch_articles(self):
        """블로그에서 최신 글 목록 가져오기"""
        articles = []
        
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            post_items = soup.find_all('div', class_='post-item')
            
            print(f"[{self.blog_id}] 총 {len(post_items)}개의 글 발견")
                    
            for item in post_items:
                link_tag = item.find('a')
                if not link_tag:
                    continue
                
                # URL 추출
                url = link_tag.get('href', '')
                
                # 제목 추출
                title_tag = item.find('h2', class_='post-title')
                title = title_tag.get_text(strip=True) if title_tag else ''
                
                # 빈 데이터 필터링
                if not title or not url:
                    continue
                
                # 날짜 추출
                date_tag = item.find('time', class_='post-author-date')
                date_str = date_tag.get_text(strip=True) if date_tag else ''
                published_at = self.parse_date(date_str)
                
                # 작성자 추출
                author_tag = item.find('span', class_='post-author-name')
                author = author_tag.get_text(strip=True) if author_tag else ''
                
                # 요약 추출
                excerpt_tag = item.find('p', class_='post-excerpt')
                excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else ''
                
                article = {
                    'blog_id': self.blog_id,
                    'title': title,
                    'url': url,
                    'author': author,
                    'excerpt': excerpt,
                    'published_at': published_at
                }
                articles.append(article)
            
        except Exception as e:
            print(f"[{self.blog_id}] 크롤링 에러: {e}")
        
        return articles
    
    def run(self):
        """크롤링 실행 및 DB 저장"""
        print(f"\n{'='*50}")
        print(f"우아한기술블로그 크롤링 시작")
        print(f"{'='*50}")
        
        # 1. 글 목록 크롤링
        articles = self.fetch_articles()
        
        if not articles:
            print("크롤링된 글이 없습니다.")
            return 0
        
        # 2. DB에 저장
        new_count = self.db.save_articles(articles)
        
        print(f"[{self.blog_id}] 크롤링 완료: 총 {len(articles)}개 중 {new_count}개 신규 저장")
        
        return new_count

if __name__ == "__main__":
    crawler = WoowahanCrawler()
    crawler.run()