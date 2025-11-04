"""
批量爬取用户信息脚本 - 正式版本
从指定UID开始递增爬取用户信息，连续遇到10个不存在的用户后停止
支持临时HTML文件清理和分批保存结果
"""

import time
import json
import os
from datetime import datetime
from ff14_spider import FF14RisingStonesSpider

class BatchSpiderProduction:
    def __init__(self, start_uid=10001009):
        """初始化批量爬虫
        
        Args:
            start_uid (int): 起始UID
        """
        self.start_uid = start_uid
        self.spider = FF14RisingStonesSpider()
        self.results = []
        self.successful_count = 0
        self.nonexistent_count = 0
        self.failed_count = 0
        self.consecutive_nonexistent = 0
        self.max_consecutive_nonexistent = 10
        self.html_files_to_delete = []
        
    def generate_url(self, uid):
        """生成用户URL"""
        return f"https://ff14risingstones.web.sdo.com/pc/index.html#/me/info?uuid={uid}"
    
    def cleanup_html_files(self):
        """删除临时HTML文件"""
        for html_file in self.html_files_to_delete:
            try:
                if os.path.exists(html_file):
                    os.remove(html_file)
                    print(f"✓ 已删除临时文件: {html_file}")
            except Exception as e:
                print(f"✗ 删除临时文件失败 {html_file}: {e}")
        self.html_files_to_delete.clear()
    
    def save_batch_results(self, batch_num):
        """保存批次结果"""
        if not self.results:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/batch_results_production_batch{batch_num}_{timestamp}.json"
        
        # 创建汇总信息
        summary = {
            "crawl_info": {
                "batch_number": batch_num,
                "start_uid": self.start_uid,
                "current_end_uid": self.start_uid + len(self.results) - 1,
                "total_crawled": len(self.results),
                "successful_users": self.successful_count,
                "nonexistent_users": self.nonexistent_count,
                "consecutive_nonexistent": self.consecutive_nonexistent,
                "failed_requests": self.failed_count,
                "crawl_time": timestamp
            },
            "results": self.results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 批次{batch_num}结果已保存到: {filename}")
            
        except Exception as e:
            print(f"✗ 保存批次{batch_num}失败: {e}")
    
    def crawl_until_nonexistent(self):
        """爬取直到连续遇到10个不存在的用户"""
        print(f"开始批量爬取用户信息 - 正式版本")
        print(f"起始UID: {self.start_uid}")
        print(f"连续{self.max_consecutive_nonexistent}个不存在用户时停止")
        print("="*50)
        
        # 启动浏览器
        if not self.spider.setup_driver():
            print("浏览器启动失败")
            return False
        
        current_uid = self.start_uid
        crawled_count = 0
        batch_count = 0
        
        try:
            while self.consecutive_nonexistent < self.max_consecutive_nonexistent:
                crawled_count += 1
                print(f"\n[{crawled_count}] 正在爬取 UID: {current_uid}")
                
                url = self.generate_url(current_uid)
                result = self.spider.scrape_url(url)
                
                if result:
                    player_data = result.get('player_data', {})
                    user_exists = player_data.get('user_exists', True)
                    
                    # 记录HTML文件用于后续删除
                    html_file = result.get('html_file')
                    if html_file:
                        self.html_files_to_delete.append(f"output/{html_file}")
                    
                    if user_exists:
                        print(f"✓ 用户存在: {player_data.get('player_id', 'Unknown')}")
                        self.successful_count += 1
                        self.consecutive_nonexistent = 0  # 重置连续不存在计数
                    else:
                        print(f"✗ 用户不存在: {player_data.get('error_message', 'Unknown error')}")
                        self.nonexistent_count += 1
                        self.consecutive_nonexistent += 1
                        print(f"   连续不存在用户数: {self.consecutive_nonexistent}")
                    
                    self.results.append(result)
                else:
                    print(f"✗ 爬取失败")
                    self.failed_count += 1
                
                current_uid += 1
                
                # 每50个用户保存一次结果（正式版本处理更多数据）
                if crawled_count % 50 == 0:
                    batch_count += 1
                    print(f"\n--- 已爬取 {crawled_count} 个用户，保存批次 {batch_count} ---")
                    self.save_batch_results(batch_count)
                    # 清理HTML文件
                    self.cleanup_html_files()
                
                # 检查是否达到连续不存在用户的限制
                if self.consecutive_nonexistent >= self.max_consecutive_nonexistent:
                    print(f"\n已连续遇到 {self.max_consecutive_nonexistent} 个不存在的用户，停止爬取")
                    break
                
                # 添加延时避免过于频繁的请求
                print("等待1秒...")
                time.sleep(1)
            
            # 保存最后一批未保存的结果
            if crawled_count % 50 != 0:
                batch_count += 1
                print(f"\n--- 保存最后批次 {batch_count} ---")
                self.save_batch_results(batch_count)
            
            # 最终清理
            self.cleanup_html_files()
            
            print(f"\n正式版本爬取完成！")
            
        except KeyboardInterrupt:
            print(f"\n用户中断爬取")
            # 中断时也要清理文件
            self.cleanup_html_files()
        except Exception as e:
            print(f"\n爬取过程中出现错误: {e}")
            # 出错时也要清理文件
            self.cleanup_html_files()
        finally:
            self.spider.close()
        
        return True
    
    def save_results(self):
        """保存爬取结果"""
        if not self.results:
            print("没有数据需要保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/batch_results_production_{timestamp}.json"
        
        # 创建汇总信息
        summary = {
            "crawl_info": {
                "start_uid": self.start_uid,
                "end_uid": self.start_uid + len(self.results) - 1,
                "total_crawled": len(self.results),
                "successful_users": self.successful_count,
                "nonexistent_users": self.nonexistent_count,
                "consecutive_nonexistent": self.consecutive_nonexistent,
                "failed_requests": self.failed_count,
                "crawl_time": timestamp
            },
            "results": self.results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ 结果已保存到: {filename}")
            self.print_summary()
            
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    
    def print_summary(self):
        """打印爬取摘要"""
        print(f"\n{'='*60}")
        print(f"批量爬取摘要 (正式版本)")
        print(f"{'='*60}")
        print(f"起始UID: {self.start_uid}")
        print(f"结束UID: {self.start_uid + len(self.results) - 1}")
        print(f"总爬取数量: {len(self.results)}")
        print(f"成功用户: {self.successful_count}")
        print(f"不存在用户: {self.nonexistent_count}")
        print(f"失败请求: {self.failed_count}")
        print(f"最终连续不存在用户数: {self.consecutive_nonexistent}")
        print(f"成功率: {(self.successful_count/len(self.results)*100) if self.results else 0:.1f}%")
        print(f"{'='*60}")
        
        # 显示成功的用户列表（只显示前10个，避免输出过长）
        if self.successful_count > 0:
            print(f"\n成功爬取的用户 (显示前10个):")
            count = 0
            for result in self.results:
                player_data = result.get('player_data', {})
                if player_data.get('user_exists', True):
                    uid = player_data.get('uid')
                    player_id = player_data.get('player_id')
                    print(f"  UID {uid}: {player_id}")
                    count += 1
                    if count >= 10:
                        if self.successful_count > 10:
                            print(f"  ... 还有 {self.successful_count - 10} 个成功用户")
                        break

def main():
    """主函数"""
    print("FF14 用户信息批量爬取器 - 正式版本")
    print("="*50)
    
    # 获取用户输入的起始UID
    try:
        start_uid_input = input("请输入起始UID (默认10001009): ").strip()
        start_uid = int(start_uid_input) if start_uid_input else 10001009
    except ValueError:
        print("输入无效，使用默认值10001009")
        start_uid = 10001009
    
    # 创建批量爬虫实例
    batch_spider = BatchSpiderProduction(start_uid=start_uid)
    
    # 开始爬取
    if batch_spider.crawl_until_nonexistent():
        # 保存结果
        batch_spider.save_results()
    else:
        print("批量爬取失败")

if __name__ == "__main__":
    main()