#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单网页爬虫程序
支持基本的网页内容抓取和解析
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleWebScraper:
    """简单网页爬虫类"""
    
    def __init__(self, timeout: int = 10, delay: float = 1.0):
        """
        初始化爬虫
        
        Args:
            timeout: 请求超时时间（秒）
            delay: 请求间隔时间（秒）
        """
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        
        # 设置请求头，模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_page_content(self, url: str) -> Optional[Dict]:
        """
        获取网页内容
        
        Args:
            url: 目标网址
            
        Returns:
            包含网页信息的字典，如果失败返回None
        """
        try:
            logger.info(f"正在抓取网页: {url}")
            
            # 添加延迟，避免请求过于频繁
            time.sleep(self.delay)
            
            # 发送请求
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 设置编码
            response.encoding = response.apparent_encoding
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取网页信息
            page_info = {
                'url': url,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'content': self._extract_main_content(soup),
                'links': self._extract_links(soup, url),
                'images': self._extract_images(soup, url),
                'status_code': response.status_code,
                'content_length': len(response.text),
                'timestamp': time.time()
            }
            
            logger.info(f"成功抓取网页，标题: {page_info['title']}")
            return page_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return None
        except Exception as e:
            logger.error(f"抓取过程中出现错误: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取网页标题"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        return "无标题"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """提取网页描述"""
        # 尝试从meta标签获取描述
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # 尝试从og:description获取
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        return "无描述"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """提取主要内容"""
        # 移除脚本和样式标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 尝试找到主要内容区域
        main_content = ""
        
        # 常见的正文容器
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '#content',
            '#main'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                main_content = content.get_text(separator='\n', strip=True)
                break
        
        # 如果没有找到特定容器，使用body内容
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body.get_text(separator='\n', strip=True)
        
        # 清理文本
        main_content = re.sub(r'\n\s*\n', '\n\n', main_content)
        main_content = re.sub(r'\s+', ' ', main_content)
        
        return main_content[:2000] + "..." if len(main_content) > 2000 else main_content
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """提取页面链接"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            
            if href and text:
                # 转换为绝对URL
                absolute_url = urljoin(base_url, href)
                links.append({
                    'text': text,
                    'url': absolute_url
                })
        
        return links[:20]  # 限制返回前20个链接
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """提取页面图片"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            alt = img.get('alt', '')
            
            if src:
                # 转换为绝对URL
                absolute_url = urljoin(base_url, src)
                images.append({
                    'src': absolute_url,
                    'alt': alt
                })
        
        return images[:10]  # 限制返回前10张图片
    
    def save_results(self, page_info: Dict, filename: str = None) -> str:
        """
        保存抓取结果
        
        Args:
            page_info: 网页信息字典
            filename: 保存的文件名，如果为None则自动生成
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            # 从URL生成文件名
            parsed_url = urlparse(page_info['url'])
            domain = parsed_url.netloc.replace('.', '_')
            filename = f"scraped_{domain}_{int(time.time())}.json"
        
        filepath = f"results/{filename}"
        
        # 确保results目录存在
        import os
        os.makedirs("results", exist_ok=True)
        
        # 保存为JSON格式
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(page_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到: {filepath}")
        return filepath


def main():
    """主函数"""
    print("=== 简单网页爬虫程序 ===")
    print("输入网址开始抓取，输入 'quit' 退出程序")
    
    scraper = SimpleWebScraper()
    
    while True:
        url = input("\n请输入要抓取的网址: ").strip()
        
        if url.lower() in ['quit', 'exit', 'q']:
            print("程序退出")
            break
        
        if not url:
            print("请输入有效的网址")
            continue
        
        # 确保URL有协议
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # 抓取网页
        page_info = scraper.get_page_content(url)
        
        if page_info:
            print(f"\n=== 抓取结果 ===")
            print(f"标题: {page_info['title']}")
            print(f"描述: {page_info['description']}")
            print(f"内容长度: {page_info['content_length']} 字符")
            print(f"链接数量: {len(page_info['links'])}")
            print(f"图片数量: {len(page_info['images'])}")
            
            # 显示部分内容
            content_preview = page_info['content'][:200] + "..." if len(page_info['content']) > 200 else page_info['content']
            print(f"\n内容预览:\n{content_preview}")
            
            # 保存结果
            try:
                filepath = scraper.save_results(page_info)
                print(f"\n结果已保存到: {filepath}")
            except Exception as e:
                print(f"保存结果时出错: {e}")
        else:
            print("抓取失败，请检查网址是否正确")


if __name__ == "__main__":
    main()