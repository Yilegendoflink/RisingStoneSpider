"""
FF14 Rising Stones 爬虫主模块
用于爬取最终幻想14官方网站的玩家信息
"""

import time
import json
import re
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FF14RisingStonesSpider:
    """FF14 Rising Stones网站爬虫"""
    
    def __init__(self, config_file='config.json'):
        """初始化爬虫
        
        Args:
            config_file (str): 配置文件路径
        """
        self.config = self.load_config(config_file)
        self.driver = None
        self.results = []
        
    def load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {config_file} 未找到，使用默认配置")
            return self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "browser": {"headless": False},
            "timeouts": {"page_load": 30, "element_wait": 10, "dynamic_content": 15},
            "selectors": {
                "player_name": [".character-name", ".player-name", "h1", "h2"],
                "server": [".server", ".world", "[class*='server']"],
                "level": [".level", "[class*='level']"],
                "job": [".job", ".class", "[class*='job']"]
            }
        }
    
    def setup_driver(self):
        """设置浏览器驱动"""
        try:
            options = Options()
            
            browser_config = self.config.get('browser', {})
            
            if browser_config.get('headless', False):
                options.add_argument('--headless')
            
            # 反检测设置
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 设置用户代理
            if 'user_agent' in browser_config:
                options.add_argument(f'--user-agent={browser_config["user_agent"]}')
            
            # 设置窗口大小
            if 'window_size' in browser_config:
                width, height = browser_config['window_size']
                options.add_argument(f'--window-size={width},{height}')
            
            self.driver = webdriver.Edge(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            print(f"浏览器启动失败: {e}")
            return False
    
    def wait_for_login(self):
        """等待用户手动登录"""
        print("\n" + "="*50)
        print("检测到需要登录")
        print("请在打开的浏览器中完成登录操作")
        print("登录完成后按Enter键继续...")
        print("="*50)
        
        input("按Enter键继续...")
        
        # 检查登录状态
        max_wait = 60
        for i in range(max_wait):
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                print("✓ 登录成功，继续爬取...")
                time.sleep(2)
                return True
            time.sleep(1)
        
        print("✗ 登录超时")
        return False
    
    def extract_player_info(self):
        """提取玩家信息"""
        player_info = {
            'url': self.driver.current_url,
            'title': self.driver.title,
            'timestamp': datetime.now().isoformat(),
            'extracted_data': {}
        }
        
        # 等待动态内容加载
        time.sleep(self.config['timeouts']['dynamic_content'])
        
        # 使用配置的选择器提取信息
        selectors = self.config.get('selectors', {})
        
        for data_type, selector_list in selectors.items():
            for selector in selector_list:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) < 100:
                            if data_type not in player_info['extracted_data']:
                                player_info['extracted_data'][data_type] = []
                            player_info['extracted_data'][data_type].append(text)
                            break
                    
                    if data_type in player_info['extracted_data']:
                        break
                        
                except NoSuchElementException:
                    continue
        
        # 保存截图
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshot_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            player_info['screenshot'] = screenshot_path
            print(f"✓ 截图已保存: {screenshot_path}")
        except Exception as e:
            print(f"✗ 截图保存失败: {e}")
        
        # 保存页面源码
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_path = f"page_source_{timestamp}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            player_info['html_file'] = html_path
            print(f"✓ 页面源码已保存: {html_path}")
        except Exception as e:
            print(f"✗ 页面源码保存失败: {e}")
        
        return player_info
    
    def scrape_url(self, url):
        """爬取单个URL"""
        print(f"\n正在爬取: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(3)
            
            current_url = self.driver.current_url
            print(f"当前页面: {current_url}")
            
            # 检查是否需要登录
            if "login" in current_url.lower():
                if not self.wait_for_login():
                    return None
            
            # 提取玩家信息
            player_info = self.extract_player_info()
            
            print("✓ 爬取完成")
            return player_info
            
        except Exception as e:
            print(f"✗ 爬取失败: {e}")
            return None
    
    def run(self, urls=None):
        """运行爬虫"""
        if not self.setup_driver():
            return False
        
        try:
            target_urls = urls or self.config.get('target_urls', [])
            
            if not target_urls:
                print("没有指定要爬取的URL")
                return False
            
            print(f"开始爬取 {len(target_urls)} 个URL...")
            
            for url in target_urls:
                result = self.scrape_url(url)
                if result:
                    self.results.append(result)
            
            # 保存结果
            self.save_results()
            
            return True
            
        finally:
            self.close()
    
    def save_results(self):
        """保存爬取结果"""
        if not self.results:
            print("没有数据需要保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"spider_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ 结果已保存到: {filename}")
            print(f"✓ 共爬取 {len(self.results)} 条数据")
            
            # 打印摘要
            print("\n爬取摘要:")
            for i, result in enumerate(self.results, 1):
                print(f"  {i}. {result.get('title', 'Unknown')}")
                extracted = result.get('extracted_data', {})
                for key, values in extracted.items():
                    if values:
                        print(f"     {key}: {values[0]}")
            
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            print("\n按任意键关闭浏览器...")
            input()
            self.driver.quit()

def main():
    """主函数"""
    print("FF14 Rising Stones 爬虫启动")
    print("="*50)
    
    spider = FF14RisingStonesSpider()
    
    # 可以传入自定义URL列表
    urls = [
        "https://ff14risingstones.web.sdo.com/pc/index.html#/me/info?uuid=10001205"
    ]
    
    success = spider.run(urls)
    
    if success:
        print("\n✓ 爬虫执行完成")
    else:
        print("\n✗ 爬虫执行失败")

if __name__ == "__main__":
    main()