"""
FF14 Rising Stones 爬虫主模块
用于爬取最终幻想14官方网站的玩家信息
"""

import time
import json
import re
import os
import pickle
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
        self.cookies_file = 'cookies.pkl'
        
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
            
            # 默认使用无头模式，除非配置中明确指定显示
            headless = browser_config.get('headless', True)
            if headless:
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
    
    def save_cookies(self):
        """保存登录态cookies"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            print("✓ 登录态已保存")
        except Exception as e:
            print(f"✗ 保存登录态失败: {e}")
    
    def load_cookies(self):
        """加载已保存的cookies"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                
                # 先访问首页以设置域名
                self.driver.get("https://ff14risingstones.web.sdo.com")
                time.sleep(2)
                
                # 添加cookies
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        continue
                
                print("✓ 登录态已加载")
                return True
        except Exception as e:
            print(f"✗ 加载登录态失败: {e}")
        return False
    
    def setup_driver_for_login(self):
        """为登录设置可见浏览器驱动"""
        print("需要重新登录，启动可见浏览器...")
        try:
            # 关闭现有的无头浏览器
            if self.driver:
                self.driver.quit()
            
            options = Options()
            browser_config = self.config.get('browser', {})
            
            # 强制显示浏览器用于登录
            # options.add_argument('--headless') 不添加这行，让浏览器可见
            
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
            print(f"启动可见浏览器失败: {e}")
            return False
    
    def wait_for_login(self):
        """等待用户手动登录"""
        # 切换到可见浏览器模式
        if not self.setup_driver_for_login():
            return False
        
        print("\n" + "="*50)
        print("检测到需要登录")
        print("已启动可见浏览器，请在浏览器中完成登录操作")
        print("登录完成后按Enter键继续...")
        print("="*50)
        
        # 重新访问登录页面
        current_url = self.driver.current_url
        self.driver.get(current_url)
        time.sleep(2)
        
        input("按Enter键继续...")
        
        # 检查登录状态
        max_wait = 60
        for i in range(max_wait):
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                print("✓ 登录成功，保存登录态...")
                self.save_cookies()
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
            'player_data': {}
        }
        
        # 等待动态内容加载
        time.sleep(self.config['timeouts']['dynamic_content'])
        
        try:
            # 获取页面所有文本内容
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in body_text.split('\n') if line.strip()]
            
            # 提取玩家ID
            player_info['player_data']['player_id'] = None
            player_info['player_data']['user_exists'] = True  # 默认用户存在
            
            for i, line in enumerate(lines):
                if line == "个人信息" and i + 1 < len(lines):
                    extracted_id = lines[i + 1]
                    player_info['player_data']['player_id'] = extracted_id
                    
                    # 检测用户是否存在
                    if extracted_id == "盛趣游戏":
                        player_info['player_data']['user_exists'] = False
                        player_info['player_data']['error_message'] = "用户不存在"
                        
                        # 从URL中提取uid
                        url_match = re.search(r'uuid=(\d+)', player_info['url'])
                        if url_match:
                            player_info['player_data']['uid'] = url_match.group(1)
                            player_info['player_data']['error_message'] = f"UID {url_match.group(1)} 对应的用户不存在"
                    
                    break
            
            # 如果用户不存在，跳过其他信息的提取
            if not player_info['player_data']['user_exists']:
                print(f"✗ 检测到用户不存在: {player_info['player_data']['error_message']}")
                # 清空其他字段
                player_info['player_data']['create_time'] = None
                player_info['player_data']['last_login'] = None
                player_info['player_data']['total_playtime'] = None
                player_info['player_data']['recent_activity'] = None
                player_info['player_data']['recent_activity_time'] = None
                player_info['player_data']['race_gender'] = None
                player_info['player_data']['fc_name'] = None
                player_info['player_data']['housing_info'] = None
                player_info['player_data']['level_info'] = None
            else:
                # 用户存在时才提取详细信息
                
                # 提取UID
                player_info['player_data']['uid'] = None
                for line in lines:
                    if line.startswith("UID:"):
                        player_info['player_data']['uid'] = line.replace("UID:", "").strip()
                        break
            
                # 提取创角时间
                player_info['player_data']['create_time'] = None
                for i, line in enumerate(lines):
                    if "创角时间" in line:
                        if "：" in line:
                            player_info['player_data']['create_time'] = line.split("：")[1].strip()
                        elif i + 1 < len(lines):
                            # 查找下一行是否是日期格式
                            next_line = lines[i + 1]
                            if re.match(r'\d{4}-\d{2}-\d{2}', next_line):
                                player_info['player_data']['create_time'] = next_line
                            # 有时候创角时间可能在前面
                            elif i > 0 and re.match(r'\d{4}-\d{2}-\d{2}', lines[i - 1]):
                                player_info['player_data']['create_time'] = lines[i - 1]
                        break
                
                # 提取最近登录时间
                player_info['player_data']['last_login'] = None
                for i, line in enumerate(lines):
                    if "最近登录时间" in line or "最近登陆时间" in line:
                        if "：" in line:
                            login_time = line.split("：")[1].strip()
                            player_info['player_data']['last_login'] = login_time if login_time else "*已屏蔽*"
                        elif i + 1 < len(lines):
                            login_time = lines[i + 1].strip()
                            player_info['player_data']['last_login'] = login_time if login_time else "*已屏蔽*"
                        break
                
                # 提取累计游戏时长
                player_info['player_data']['total_playtime'] = None
                for i, line in enumerate(lines):
                    if "累计游戏时长" in line:
                        if "：" in line:
                            player_info['player_data']['total_playtime'] = line.split("：")[1].strip()
                        else:
                            # 查找包含时长信息的行
                            for j in range(max(0, i - 2), min(i + 3, len(lines))):
                                if "天" in lines[j] and ("小时" in lines[j] or "分钟" in lines[j]):
                                    player_info['player_data']['total_playtime'] = lines[j]
                                    break
                        break
                
                # 提取游戏近况
                player_info['player_data']['recent_activity'] = None
                player_info['player_data']['recent_activity_time'] = None
                
                for i, line in enumerate(lines):
                    if "游戏近况" in line:
                        # 查找后续的活动信息
                        for j in range(i + 1, min(i + 5, len(lines))):
                            if lines[j] and not lines[j] in ["游戏近况", "TA的帖子", "TA的动态"]:
                                # 检查是否是时间格式
                                if re.match(r'\d{4}-\d{2}-\d{2}', lines[j]):
                                    player_info['player_data']['recent_activity_time'] = lines[j]
                                else:
                                    player_info['player_data']['recent_activity'] = lines[j]
                                
                                # 如果找到了活动描述，继续查找时间
                                if player_info['player_data']['recent_activity'] and not player_info['player_data']['recent_activity_time']:
                                    for k in range(j + 1, min(j + 3, len(lines))):
                                        if re.match(r'\d{4}-\d{2}-\d{2}', lines[k]):
                                            player_info['player_data']['recent_activity_time'] = lines[k]
                                            break
                                break
                        break
                
                # 如果游戏近况为空，标记为空
                if not player_info['player_data']['recent_activity']:
                    player_info['player_data']['recent_activity'] = "无近期活动"
                
                # 提取其他角色信息 - 使用更精确的匹配
                player_info['player_data']['race_gender'] = None
                player_info['player_data']['fc_name'] = None
                player_info['player_data']['housing_info'] = None
                
                # 查找包含"敖龙族"等种族信息的行
                for line in lines:
                    if any(race in line for race in ["敖龙族", "猫魅族", "拉拉菲尔", "鲁加丁", "精灵族", "人族"]):
                        if "种族性别：" in line:
                            player_info['player_data']['race_gender'] = line.split("：")[1].strip()
                        else:
                            player_info['player_data']['race_gender'] = line.strip()
                        break
                
                # 查找部队信息 - 寻找包含<>的行
                for line in lines:
                    if "<" in line and ">" in line and "無我夢中" in line:
                        if "部队名称：" in line:
                            player_info['player_data']['fc_name'] = line.split("：")[1].strip()
                        else:
                            player_info['player_data']['fc_name'] = line.strip()
                        break
                
                # 查找房屋信息
                for line in lines:
                    if "高脚孤丘" in line or "薰衣草苗圃" in line or any(area in line for area in ["M", "S", "L"]):
                        if "房屋信息：" in line:
                            player_info['player_data']['housing_info'] = line.split("：")[1].strip()
                        elif line.strip() and len(line.strip()) < 20:  # 避免过长的文本
                            player_info['player_data']['housing_info'] = line.strip()
                        break
                
                # 提取等级信息（如果有的话）
                level_info = []
                for line in lines:
                    if "LV" in line and "冒险者" in line:
                        level_info.append(line)
                
                if level_info:
                    player_info['player_data']['level_info'] = level_info
            
        except Exception as e:
            print(f"提取玩家信息时出错: {e}")
        
        # 保存页面源码
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_path = f"output/page_source_{timestamp}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            player_info['html_file'] = f"page_source_{timestamp}.html"
            print(f"✓ 页面源码已保存: {html_path}")
        except Exception as e:
            print(f"✗ 页面源码保存失败: {e}")
        
        return player_info
    
    def scrape_url(self, url):
        """爬取单个URL"""
        print(f"\n正在爬取: {url}")
        
        try:
            # 尝试加载已保存的登录态
            if self.load_cookies():
                print("使用已保存的登录态")
            
            # 直接访问目标URL
            self.driver.get(url)
            time.sleep(3)
            
            current_url = self.driver.current_url
            print(f"当前页面: {current_url}")
            
            # 检查是否需要登录
            if "login" in current_url.lower():
                if not self.wait_for_login():
                    return None
                
                # 登录成功后重新访问目标URL
                print(f"重新访问目标页面: {url}")
                self.driver.get(url)
                time.sleep(5)
                
                # 再次检查URL
                current_url = self.driver.current_url
                print(f"登录后访问页面: {current_url}")
                
                # 如果还是首页，尝试通过导航访问目标页面
                if current_url != url and "#/me/info" not in current_url:
                    print("尝试通过JavaScript导航到目标页面...")
                    self.driver.execute_script(f"window.location.href = '{url}';")
                    time.sleep(5)
                    current_url = self.driver.current_url
                    print(f"JavaScript导航后页面: {current_url}")
            
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
        filename = f"output/spider_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ 结果已保存到: {filename}")
            print(f"✓ 共爬取 {len(self.results)} 条数据")
            
            # 打印摘要
            print("\n爬取摘要:")
            for i, result in enumerate(self.results, 1):
                player_data = result.get('player_data', {})
                print(f"  {i}. {result.get('title', 'Unknown')}")
                
                if not player_data.get('user_exists', True):
                    print(f"     ❌ {player_data.get('error_message', '用户不存在')}")
                    print(f"     请求的UID: {player_data.get('uid', 'N/A')}")
                else:
                    print(f"     ✓ 用户存在")
                    print(f"     玩家ID: {player_data.get('player_id', 'N/A')}")
                    print(f"     UID: {player_data.get('uid', 'N/A')}")
                    print(f"     创角时间: {player_data.get('create_time', 'N/A')}")
                    print(f"     最近登录: {player_data.get('last_login', 'N/A')}")
                    print(f"     游戏时长: {player_data.get('total_playtime', 'N/A')}")
                    print(f"     最近活动: {player_data.get('recent_activity', 'N/A')}")
                    if player_data.get('recent_activity_time'):
                        print(f"     活动时间: {player_data.get('recent_activity_time', 'N/A')}")
                    print(f"     种族性别: {player_data.get('race_gender', 'N/A')}")
                    print(f"     部队名称: {player_data.get('fc_name', 'N/A')}")
            
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            print("正在关闭浏览器...")
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