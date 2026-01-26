
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from database import Database
import json
import sys
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 상위 폴더의 .env를 import하기 위해 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

class BlogCrawler:
    def __init__(self):
        self.db = Database()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
    
    def send_slack_notification(self, total_new, details):
        """Slack으로 크롤링 결과 알림 전송"""
        if not self.slack_webhook:
            print("Slack Webhook URL이 설정되지 않았습니다.")
            return
        
        if total_new == 0:
            message = "🔍 *기술 블로그 크롤링 완료*\n새로운 글이 없습니다."
        else:
            message = f"🎉 *기술 블로그 크롤링 완료*\n총 *{total_new}개* 새 글 발견!\n\n"
            for detail in details:
                if detail['new_count'] > 0:
                    message += f"• {detail['blog_name']}: {detail['new_count']}개\n"
        
        payload = {
            'text': message,
            'username': '기술블로그 봇',
            'icon_emoji': ':robot_face:'
        }
        
        try:
            response = requests.post(
                self.slack_webhook,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                verify=False
            )
            if response.status_code == 200:
                print("Slack 알림 전송 성공!")
            else:
                print(f"Slack 알림 실패: {response.status_code}")
        except Exception as e:
            print(f"Slack 알림 에러: {e}")
    
    def crawl_woowahan(self):
        """우아한기술블로그 크롤링 (HTML)"""
        blog_id = 'woowahan'
        blog_name = '우아한기술블로그'
        url = 'https://techblog.woowahan.com/'
        articles = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            post_items = soup.find_all('div', class_='post-item')
            
            for item in post_items:
                link_tag = item.find('a')
                if not link_tag:
                    continue
                
                article_url = link_tag.get('href', '')
                title_tag = item.find('h2', class_='post-title')
                title = title_tag.get_text(strip=True) if title_tag else ''
                
                if not title or not article_url:
                    continue
                
                date_tag = item.find('time', class_='post-author-date')
                date_str = date_tag.get_text(strip=True) if date_tag else ''
                
                author_tag = item.find('span', class_='post-author-name')
                author = author_tag.get_text(strip=True) if author_tag else ''
                
                excerpt_tag = item.find('p', class_='post-excerpt')
                excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else ''
                
                published_at = None
                try:
                    published_at = datetime.strptime(date_str, '%b.%d.%Y')
                except:
                    pass
                
                articles.append({
                    'blog_id': blog_id,
                    'title': title,
                    'url': article_url,
                    'author': author,
                    'excerpt': excerpt,
                    'published_at': published_at
                })
            
            print(f"[{blog_name}] {len(articles)}개 글 발견")
            
        except Exception as e:
            print(f"[{blog_name}] 크롤링 에러: {e}")
        
        return articles, blog_name
    
    def crawl_kakao(self):
        """카카오 테크 블로그 크롤링 (RSS)"""
        blog_id = 'kakao'
        blog_name = 'Kakao Tech'
        url = 'https://tech.kakao.com/feed/'
        articles = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item')
            
            for item in items:
                title = item.find('title').get_text(strip=True) if item.find('title') else ''
                link = item.find('link').get_text(strip=True) if item.find('link') else ''
                
                if not title or not link:
                    continue
                
                # 작성자
                creator = item.find('dc:creator')
                author = creator.get_text(strip=True) if creator else ''
                
                # 요약
                description = item.find('description')
                excerpt = ''
                if description:
                    desc_soup = BeautifulSoup(description.get_text(), 'html.parser')
                    excerpt = desc_soup.get_text(strip=True)[:200]
                
                # 날짜 (Tue, 14 Jan 2025 00:00:00 +0000 형식)
                pub_date = item.find('pubDate')
                published_at = None
                if pub_date:
                    try:
                        date_str = pub_date.get_text(strip=True)
                        published_at = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                    except:
                        pass
                
                articles.append({
                    'blog_id': blog_id,
                    'title': title,
                    'url': link,
                    'author': author,
                    'excerpt': excerpt,
                    'published_at': published_at
                })
            
            print(f"[{blog_name}] {len(articles)}개 글 발견")
            
        except Exception as e:
            print(f"[{blog_name}] 크롤링 에러: {e}")
        
        return articles, blog_name
    
    def crawl_naver(self):
        """네이버 D2 크롤링 (RSS)"""
        blog_id = 'naver'
        blog_name = 'NAVER D2'
        url = 'https://d2.naver.com/d2.atom'
        articles = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'xml')
            entries = soup.find_all('entry')
            
            for entry in entries:
                title = entry.find('title').get_text(strip=True) if entry.find('title') else ''
                link_tag = entry.find('link')
                link = link_tag.get('href', '') if link_tag else ''
                
                if not title or not link:
                    continue
                
                # 요약
                content = entry.find('content')
                excerpt = ''
                if content:
                    content_soup = BeautifulSoup(content.get_text(), 'html.parser')
                    excerpt = content_soup.get_text(strip=True)[:200]
                
                # 날짜 (2026-01-14T10:57:09Z 형식)
                updated = entry.find('updated')
                published_at = None
                if updated:
                    try:
                        date_str = updated.get_text(strip=True)
                        published_at = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                    except:
                        pass
                
                articles.append({
                    'blog_id': blog_id,
                    'title': title,
                    'url': link,
                    'author': '',
                    'excerpt': excerpt,
                    'published_at': published_at
                })
            
            print(f"[{blog_name}] {len(articles)}개 글 발견")
            
        except Exception as e:
            print(f"[{blog_name}] 크롤링 에러: {e}")
        
        return articles, blog_name
    
    def crawl_oliveyoung(self):
        """올리브영 기술블로그 크롤링 (RSS)"""
        blog_id = 'oliveyoung'
        blog_name = '올리브영 기술블로그'
        url = 'https://oliveyoung.tech/rss.xml'
        articles = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item')
            
            for item in items:
                title = item.find('title').get_text(strip=True) if item.find('title') else ''
                link = item.find('link').get_text(strip=True) if item.find('link') else ''
                
                if not title or not link:
                    continue
                
                # 요약
                description = item.find('description')
                excerpt = ''
                if description:
                    desc_soup = BeautifulSoup(description.get_text(), 'html.parser')
                    excerpt = desc_soup.get_text(strip=True)[:200]
                
                # 날짜
                pub_date = item.find('pubDate')
                published_at = None
                if pub_date:
                    try:
                        date_str = pub_date.get_text(strip=True)
                        published_at = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                    except:
                        pass
                
                articles.append({
                    'blog_id': blog_id,
                    'title': title,
                    'url': link,
                    'author': '',
                    'excerpt': excerpt,
                    'published_at': published_at
                })
            
            print(f"[{blog_name}] {len(articles)}개 글 발견")
            
        except Exception as e:
            print(f"[{blog_name}] 크롤링 에러: {e}")
        
        return articles, blog_name
    
    def crawl_yanolja(self):
        """야놀자 기술블로그 크롤링 (Medium RSS)"""
        blog_id = 'yanolja'
        blog_name = '야놀자 기술블로그'
        url = 'https://medium.com/feed/yanoljacloud-tech'
        articles = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item')
            
            for item in items:
                title = item.find('title').get_text(strip=True) if item.find('title') else ''
                link = item.find('link').get_text(strip=True) if item.find('link') else ''
                
                if not title or not link:
                    continue
                
                # 작성자 (Medium은 dc:creator 사용)
                creator = item.find('dc:creator')
                author = creator.get_text(strip=True) if creator else ''
                
                # 요약
                description = item.find('description')
                excerpt = ''
                if description:
                    desc_soup = BeautifulSoup(description.get_text(), 'html.parser')
                    excerpt = desc_soup.get_text(strip=True)[:200]
                
                # 날짜 (Medium RSS 형식: Tue, 14 Jan 2025 00:00:00 GMT)
                pub_date = item.find('pubDate')
                published_at = None
                if pub_date:
                    try:
                        date_str = pub_date.get_text(strip=True)
                        published_at = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
                    except:
                        pass
                
                articles.append({
                    'blog_id': blog_id,
                    'title': title,
                    'url': link,
                    'author': author,
                    'excerpt': excerpt,
                    'published_at': published_at
                })
            
            print(f"[{blog_name}] {len(articles)}개 글 발견")
            
        except Exception as e:
            print(f"[{blog_name}] 크롤링 에러: {e}")
        
        return articles, blog_name


    def run_all(self):
        """모든 블로그 크롤링 실행"""
        print("=" * 50)
        print("기술 블로그 크롤링 시작")
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        total_new = 0
        details = []
        
        # 각 블로그 크롤링
        crawlers = [
            self.crawl_woowahan,
            self.crawl_kakao,
            self.crawl_naver,
            self.crawl_oliveyoung,
            self.crawl_yanolja,
        ]
        
        for crawl_func in crawlers:
            articles, blog_name = crawl_func()
            new_count = 0
            
            if articles:
                new_count = self.db.save_articles(articles)
                print(f"[{blog_name}] {new_count}개 신규 저장")
            
            details.append({
                'blog_name': blog_name,
                'new_count': new_count
            })
            total_new += new_count
        
        print("=" * 50)
        print(f"크롤링 완료! 총 {total_new}개 신규 글 저장")
        print("=" * 50)
        
        # Slack 알림 전송
        self.send_slack_notification(total_new, details)
        
        return total_new

if __name__ == "__main__":
    crawler = BlogCrawler()
    crawler.run_all()