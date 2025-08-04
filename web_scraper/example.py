#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫程序使用示例
"""

from simple_scraper import SimpleWebScraper


def example_usage():
    """使用示例"""
    print("=== 爬虫程序使用示例 ===")
    
    # 创建爬虫实例
    scraper = SimpleWebScraper(timeout=10, delay=1.0)
    
    # 示例网址
    test_urls = [
        "https://www.python.org",
        "https://httpbin.org/html",
        "https://example.com"
    ]
    
    for url in test_urls:
        print(f"\n正在抓取: {url}")
        
        # 抓取网页内容
        page_info = scraper.get_page_content(url)
        
        if page_info:
            print(f"✓ 成功抓取")
            print(f"  标题: {page_info['title']}")
            print(f"  描述: {page_info['description'][:100]}...")
            print(f"  内容长度: {page_info['content_length']} 字符")
            
            # 保存结果
            filepath = scraper.save_results(page_info)
            print(f"  结果已保存: {filepath}")
        else:
            print(f"✗ 抓取失败")


if __name__ == "__main__":
    example_usage()