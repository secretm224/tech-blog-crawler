#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 연결 테스트 스크립트
실제 MySQL 연결을 테스트하고 기본 데이터를 확인합니다.
"""

import sys
import logging
from crawler.database import db, DatabaseContext

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def test_database():
    """데이터베이스 연결 및 기본 기능 테스트"""
    print("🔍 데이터베이스 연결 테스트 시작...")
    print("=" * 50)
    
    try:
        # 데이터베이스 연결 테스트
        with DatabaseContext():
            # 1. 연결 테스트
            if not db.test_connection():
                print("❌ 데이터베이스 연결 실패!")
                return False
            
            # 2. 블로그 목록 조회
            print("\n📚 등록된 블로그 목록:")
            blogs = db.get_blogs()
            
            if not blogs:
                print("⚠️ 등록된 블로그가 없습니다.")
                print("MySQL에서 블로그 데이터를 먼저 삽입해주세요:")
                print("INSERT INTO blogs (blog_id, blog_name, blog_url) VALUES ...")
                return False
            
            for blog in blogs:
                print(f"  - {blog['blog_name']} ({blog['blog_id']})")
                print(f"    URL: {blog['blog_url']}")
            
            print(f"\n✅ 데이터베이스 테스트 완료!")
            print(f"   - 등록된 블로그: {len(blogs)}개")
            
            return True
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        print("\n🔧 해결 방법:")
        print("1. .env 파일의 DB 정보가 정확한지 확인")
        print("2. MySQL 서버가 실행 중인지 확인") 
        print("3. 데이터베이스 스키마가 생성되어 있는지 확인")
        print("4. AWS RDS 보안그룹 설정 확인")
        return False


def show_config_info():
    """현재 설정 정보 표시"""
    from config import config
    
    print("\n⚙️ 현재 설정 정보:")
    print("-" * 30)
    print(f"DB Host: {config.DB_HOST}")
    print(f"DB User: {config.DB_USER}")
    print(f"DB Name: {config.DB_NAME}")
    print(f"DB Port: {config.DB_PORT}")
    print(f"Password: {'***' if config.DB_PASSWORD else '(없음)'}")


if __name__ == "__main__":
    # 설정 정보 표시
    show_config_info()
    
    # 데이터베이스 테스트 실행
    success = test_database()
    
    if success:
        print("\n🎉 모든 테스트 통과! 다음 단계로 진행 가능합니다.")
        sys.exit(0)
    else:
        print("\n💥 테스트 실패! 설정을 확인하고 다시 시도해주세요.")
        sys.exit(1)
