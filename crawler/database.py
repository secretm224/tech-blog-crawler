# crawler/database.py

import sys
import os
import pymysql
import hashlib

# 상위 폴더의 config.py를 import하기 위해 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class Database:
    def __init__(self):
        self.config = Config.get_db_config()
    
    def get_connection(self):
        return pymysql.connect(**self.config)
    
    def generate_article_id(self, url):
        """URL로 고유 article_id 생성 (MD5 해시)"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_all_blogs(self):
        """등록된 모든 블로그 조회"""
        conn = self.get_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM blogs WHERE is_active = TRUE")
                return cursor.fetchall()
        finally:
            conn.close()
    
    def get_existing_urls(self, blog_id):
        """해당 블로그의 기존 글 URL 목록 조회"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT url FROM articles WHERE blog_id = %s",
                    (blog_id,)
                )
                return {row[0] for row in cursor.fetchall()}
        finally:
            conn.close()
    
    def save_articles(self, articles):
        """새 글 저장 및 신규 글 개수 반환"""
        if not articles:
            return 0
        
        conn = self.get_connection()
        new_count = 0
        
        try:
            blog_id = articles[0]['blog_id']
            existing_urls = self.get_existing_urls(blog_id)
            
            with conn.cursor() as cursor:
                for article in articles:
                    # 빈 데이터 필터링
                    if not article['title'] or not article['url']:
                        continue
                    
                    # 중복 체크
                    if article['url'] in existing_urls:
                        continue
                    
                    # article_id 생성
                    article_id = self.generate_article_id(article['url'])
                    
                    # published_date 문자열 변환
                    published_date = None
                    if article['published_at']:
                        published_date = article['published_at'].strftime('%Y-%m-%d')
                    
                    # 새 글 저장
                    cursor.execute("""
                        INSERT INTO articles 
                        (article_id, blog_id, title, url, summary, author, published_date, is_new)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                    """, (
                        article_id,
                        article['blog_id'],
                        article['title'],
                        article['url'],
                        article['excerpt'],
                        article['author'],
                        published_date
                    ))
                    new_count += 1
                
                # 블로그 통계 업데이트
                if new_count > 0:
                    cursor.execute("""
                        UPDATE blogs 
                        SET new_article_count = new_article_count + %s,
                            total_article_count = total_article_count + %s,
                            last_crawled_at = NOW()
                        WHERE blog_id = %s
                    """, (new_count, new_count, blog_id))
                
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            print(f"DB 저장 에러: {e}")
            raise
        finally:
            conn.close()
        
        return new_count

if __name__ == "__main__":
    db = Database()
    blogs = db.get_all_blogs()
    print("등록된 블로그:")
    for blog in blogs:
        print(f"  - {blog['blog_name']}")