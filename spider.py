#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RisingStoneSpider - 论坛用户信息爬虫
用于根据UID爬取特定论坛的用户个人信息页信息
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class ForumSpider:
    """论坛用户信息爬虫类"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化爬虫
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.session = self._create_session()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"配置文件不存在: {config_path}")
            raise
        except json.JSONDecodeError:
            logging.error(f"配置文件格式错误: {config_path}")
            raise
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('spider.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _create_session(self) -> requests.Session:
        """创建HTTP会话"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.config.get('user_agent', 'Mozilla/5.0')
        })
        return session
    
    def fetch_user_info(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        根据UID获取用户信息
        
        Args:
            uid: 用户ID
            
        Returns:
            用户信息字典，获取失败返回None
        """
        url = self._build_profile_url(uid)
        max_retries = self.config.get('max_retries', 3)
        timeout = self.config.get('timeout', 10)
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"正在获取用户 {uid} 的信息 (尝试 {attempt + 1}/{max_retries})")
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                
                # 解析用户信息
                user_info = self._parse_user_profile(response.text, uid)
                user_info['fetch_time'] = datetime.now().isoformat()
                
                self.logger.info(f"成功获取用户 {uid} 的信息")
                return user_info
                
            except requests.RequestException as e:
                self.logger.warning(f"获取用户 {uid} 信息失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    self.logger.error(f"用户 {uid} 信息获取失败，已达最大重试次数")
                    return None
            except Exception as e:
                self.logger.error(f"解析用户 {uid} 信息时出错: {e}")
                return None
    
    def _build_profile_url(self, uid: str) -> str:
        """构建用户个人信息页URL"""
        base_url = self.config.get('forum_url', '')
        if not base_url:
            raise ValueError("配置中缺少 'forum_url'，请检查配置文件")
        profile_path = self.config.get('user_profile_path', '/user/profile/{uid}')
        profile_path = profile_path.format(uid=uid)
        return base_url.rstrip('/') + profile_path
    
    def _parse_user_profile(self, html: str, uid: str) -> Dict[str, Any]:
        """
        解析用户个人信息页
        
        Args:
            html: 网页HTML内容
            uid: 用户ID
            
        Returns:
            解析后的用户信息字典
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 基本信息提取（需要根据实际论坛结构调整）
        user_info = {
            'uid': uid,
            'username': self._extract_text(soup, '.username'),
            'posts_count': self._extract_text(soup, '.posts-count'),
            'registration_date': self._extract_text(soup, '.registration-date'),
            'last_active': self._extract_text(soup, '.last-active'),
            'reputation': self._extract_text(soup, '.reputation'),
            'profile_url': self._build_profile_url(uid)
        }
        
        return user_info
    
    def _extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """
        从HTML中提取文本
        
        Args:
            soup: BeautifulSoup对象
            selector: CSS选择器
            
        Returns:
            提取的文本，失败返回空字符串
        """
        try:
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else ""
        except Exception:
            return ""
    
    def fetch_multiple_users(self, uid_list: List[str]) -> List[Dict[str, Any]]:
        """
        批量获取多个用户信息
        
        Args:
            uid_list: 用户ID列表
            
        Returns:
            用户信息列表
        """
        results = []
        rate_limit = self.config.get('rate_limit_seconds', 1)
        
        for i, uid in enumerate(uid_list):
            self.logger.info(f"进度: {i + 1}/{len(uid_list)}")
            user_info = self.fetch_user_info(uid)
            
            if user_info:
                results.append(user_info)
            
            # 速率限制
            if i < len(uid_list) - 1:
                time.sleep(rate_limit)
        
        return results
    
    def save_results(self, data: List[Dict[str, Any]], filename: str = None):
        """
        保存爬取结果
        
        Args:
            data: 用户信息列表
            filename: 保存文件名（可选）
        """
        output_dir = self.config.get('output_dir', 'data')
        output_format = self.config.get('output_format', 'json')
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"user_data_{timestamp}"
        
        filepath = os.path.join(output_dir, f"{filename}.{output_format}")
        
        try:
            if output_format == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif output_format == 'csv':
                if data:
                    keys = data[0].keys()
                    with open(filepath, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=keys)
                        writer.writeheader()
                        writer.writerows(data)
            
            self.logger.info(f"数据已保存到: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            raise
    
    def get_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        统计用户数据
        
        Args:
            data: 用户信息列表
            
        Returns:
            统计信息字典
        """
        if not data:
            return {}
        
        stats = {
            'total_users': len(data),
            'successful_fetches': len([u for u in data if u.get('username')]),
            'failed_fetches': len([u for u in data if not u.get('username')]),
        }
        
        # 计算总帖子数（如果有）
        posts_counts = [int(u.get('posts_count', 0)) for u in data 
                       if u.get('posts_count', '').isdigit()]
        if posts_counts:
            stats['total_posts'] = sum(posts_counts)
            stats['average_posts'] = sum(posts_counts) / len(posts_counts)
        
        return stats
