#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
크롤러 설정 관리
환경변수를 불러와서 설정값을 관리합니다.
"""

import os
from dotenv import load_dotenv

# .env 파일 로드 (로컬 개발시)
load_dotenv()


class Config:
    """설정 클래스"""
    
    # 데이터베이스 설정
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'secretm_db')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # 크롤링 설정
    CRAWL_DELAY = int(os.getenv('CRAWL_DELAY', 2))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 15))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    
    # 로그 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # User-Agent
    USER_AGENT = os.getenv('USER_AGENT', 
        'Mozilla/5.0 (compatible; TechBlogCrawler/1.0)')
    
    # 지원하는 블로그 목록
    SUPPORTED_BLOGS = {
        'woowahan': {
            'name': '우아한기술블로그',
            'url': 'https://techblog.woowahan.com/',
            'enabled': True
        },
        'oliveyoung': {
            'name': '올리브영 기술블로그',
            'url': 'https://oliveyoung.tech/',
            'enabled': True
        },
        'kakao': {
            'name': 'Kakao Tech',
            'url': 'https://tech.kakao.com/',
            'enabled': True
        },
        'naver': {
            'name': 'NAVER D2',
            'url': 'https://d2.naver.com/',
            'enabled': True
        }
    }
    
    @classmethod
    def get_db_config(cls):
        """DB 설정 딕셔너리 반환"""
        return {
            'host': cls.DB_HOST,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'port': cls.DB_PORT,
            'charset': 'utf8mb4',
            'autocommit': True
        }
    
    @classmethod
    def get_enabled_blogs(cls):
        """활성화된 블로그 목록 반환"""
        return {k: v for k, v in cls.SUPPORTED_BLOGS.items() if v['enabled']}
    
    @classmethod
    def validate_config(cls):
        """설정값 유효성 검사"""
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"필수 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        
        return True


# 설정 인스턴스 (중요!)
config = Config()