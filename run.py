"""
快速启动脚本
"""

from ff14_spider import FF14RisingStonesSpider

def quick_start():
    """快速启动爬虫"""
    print("FF14 Rising Stones 爬虫 - 快速启动")
    print("="*40)
    
    # 获取用户输入的URL（可选）
    url_input = input("请输入要爬取的URL（直接回车使用默认URL）: ").strip()
    
    spider = FF14RisingStonesSpider()
    
    if url_input:
        urls = [url_input]
        success = spider.run(urls)
    else:
        success = spider.run()
    
    if success:
        print("\n爬取完成！")
    else:
        print("\n爬取失败！")

if __name__ == "__main__":
    quick_start()