"""
页面信息分析脚本
用于分析FF14页面结构，确定各项信息的位置
"""

import time
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import NoSuchElementException
import pickle
import os

class PageAnalyzer:
    def __init__(self):
        """初始化页面分析器"""
        self.options = Options()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.driver = None
        self.cookies_file = 'analyzer_cookies.pkl'
        
    def start_driver(self):
        """启动浏览器"""
        self.driver = webdriver.Edge(options=self.options)
        return self.driver
        
    def load_cookies(self):
        """加载已保存的cookies"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                
                self.driver.get("https://ff14risingstones.web.sdo.com")
                time.sleep(2)
                
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        continue
                
                print("✓ 分析器登录态已加载")
                return True
        except Exception as e:
            print(f"✗ 加载分析器登录态失败: {e}")
        return False
    
    def save_cookies(self):
        """保存登录态cookies"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            print("✓ 分析器登录态已保存")
        except Exception as e:
            print(f"✗ 保存分析器登录态失败: {e}")
    
    def wait_for_login(self):
        """等待用户手动登录"""
        print("\n" + "="*50)
        print("分析器检测到需要登录")
        print("请在打开的浏览器中完成登录操作")
        print("登录完成后按Enter键继续...")
        print("="*50)
        
        input("按Enter键继续...")
        
        # 检查登录状态
        max_wait = 60
        for i in range(max_wait):
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                print("✓ 登录成功，保存分析器登录态...")
                self.save_cookies()
                time.sleep(2)
                return True
            time.sleep(1)
        
        print("✗ 登录超时")
        return False
    
    def analyze_page_structure(self, url):
        """分析页面结构"""
        print(f"正在分析页面: {url}")
        
        # 加载登录态
        if self.load_cookies():
            print("使用已保存的分析器登录态")
        
        # 访问页面
        self.driver.get(url)
        time.sleep(3)
        
        current_url = self.driver.current_url
        print(f"当前URL: {current_url}")
        
        # 检查是否需要登录
        if "login" in current_url.lower():
            if not self.wait_for_login():
                return None
            
            # 登录成功后重新访问目标URL
            print(f"重新访问目标页面: {url}")
            self.driver.get(url)
            time.sleep(5)
            current_url = self.driver.current_url
            print(f"登录后访问页面: {current_url}")
        
        print(f"页面标题: {self.driver.title}")
        time.sleep(5)  # 等待页面完全加载
        
        # 获取页面源码
        page_source = self.driver.page_source
        
        # 保存完整页面源码
        with open('output/page_analysis.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("✓ 完整页面源码已保存到 output/page_analysis.html")
        
        # 分析页面文本内容
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        lines = body_text.split('\n')
        
        analysis_result = {
            'url': self.driver.current_url,
            'title': self.driver.title,
            'all_text_lines': [line.strip() for line in lines if line.strip()],
            'found_elements': {}
        }
        
        # 查找关键信息
        keywords = {
            'player_id': ['玩家ID', 'ID', '角色名'],
            'create_time': ['创角时间', '创建时间', '注册时间'],
            'last_login': ['最近登陆', '最后登录', '上次登录'],
            'total_playtime': ['累计游戏时长', '游戏时长', '总时长'],
            'recent_activity': ['游戏近况', '最近活动', '达成']
        }
        
        # 搜索包含关键词的文本
        for category, keyword_list in keywords.items():
            found_info = []
            for line in lines:
                line = line.strip()
                if any(keyword in line for keyword in keyword_list):
                    found_info.append(line)
            if found_info:
                analysis_result['found_elements'][category] = found_info
        
        # 尝试通过不同的选择器查找元素
        selectors_to_try = [
            # 常见的信息容器
            ".info", ".profile", ".detail", ".content", ".player-info",
            ".character-info", ".user-info", ".game-info",
            # 表格和列表
            "table", "tr", "td", "ul", "li", "dl", "dt", "dd",
            # 文本容器
            "div", "span", "p", "h1", "h2", "h3", "h4", "h5", "h6",
            # 特定属性
            "[class*='time']", "[class*='date']", "[class*='play']",
            "[class*='activity']", "[class*='recent']"
        ]
        
        element_analysis = {}
        for selector in selectors_to_try:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    element_texts = []
                    for i, element in enumerate(elements[:10]):  # 限制前10个元素
                        text = element.text.strip()
                        if text and len(text) < 500:  # 过滤过长文本
                            element_texts.append({
                                'index': i,
                                'text': text,
                                'tag': element.tag_name,
                                'class': element.get_attribute('class') or '',
                                'id': element.get_attribute('id') or ''
                            })
                    
                    if element_texts:
                        element_analysis[selector] = element_texts
                        
            except Exception as e:
                continue
        
        analysis_result['element_analysis'] = element_analysis
        
        # 保存分析结果
        with open('output/page_structure_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        print("✓ 页面结构分析完成，结果保存到 output/page_structure_analysis.json")
        
        # 打印关键发现
        print("\n=== 关键信息发现 ===")
        for category, info_list in analysis_result['found_elements'].items():
            print(f"{category}:")
            for info in info_list:
                print(f"  - {info}")
        
        return analysis_result
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            print("正在关闭分析器浏览器...")
            self.driver.quit()

def main():
    """主函数"""
    print("FF14 页面结构分析器")
    print("="*50)
    
    analyzer = PageAnalyzer()
    
    try:
        analyzer.start_driver()
        
        # 分析目标页面
        url = "https://ff14risingstones.web.sdo.com/pc/index.html#/me/info?uuid=10001009"
        result = analyzer.analyze_page_structure(url)
        
        print("\n分析完成！请查看 output/ 文件夹中的分析结果")
        
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()