#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RisingStoneSpider 主程序入口
"""

import argparse
import json
from spider import ForumSpider


def main():
    parser = argparse.ArgumentParser(
        description='RisingStoneSpider - 论坛用户信息爬虫',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 爬取单个用户信息
  python main.py --uid 12345
  
  # 爬取多个用户信息
  python main.py --uid 12345 23456 34567
  
  # 从文件读取UID列表
  python main.py --uid-file uids.txt
  
  # 指定输出文件名
  python main.py --uid 12345 --output my_data
  
  # 使用自定义配置文件
  python main.py --uid 12345 --config custom_config.json
        """
    )
    
    parser.add_argument(
        '--uid',
        nargs='+',
        help='用户UID，可以指定多个，用空格分隔'
    )
    
    parser.add_argument(
        '--uid-file',
        help='包含UID列表的文件路径，每行一个UID'
    )
    
    parser.add_argument(
        '--output',
        help='输出文件名（不含扩展名）'
    )
    
    parser.add_argument(
        '--config',
        default='config.json',
        help='配置文件路径（默认: config.json）'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='显示统计信息'
    )
    
    args = parser.parse_args()
    
    # 获取UID列表
    uid_list = []
    
    if args.uid:
        uid_list.extend(args.uid)
    
    if args.uid_file:
        try:
            with open(args.uid_file, 'r', encoding='utf-8') as f:
                uid_list.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print(f"错误: 文件 '{args.uid_file}' 不存在")
            return
    
    if not uid_list:
        parser.print_help()
        print("\n错误: 必须提供至少一个UID（使用 --uid 或 --uid-file）")
        return
    
    # 初始化爬虫
    try:
        spider = ForumSpider(args.config)
    except Exception as e:
        print(f"错误: 初始化爬虫失败 - {e}")
        return
    
    # 爬取数据
    print(f"开始爬取 {len(uid_list)} 个用户的信息...")
    results = spider.fetch_multiple_users(uid_list)
    
    # 保存结果
    if results:
        try:
            filepath = spider.save_results(results, args.output)
            print(f"\n成功! 数据已保存到: {filepath}")
            print(f"共爬取 {len(results)} 个用户的信息")
            
            # 显示统计信息
            if args.stats:
                stats = spider.get_statistics(results)
                print("\n=== 统计信息 ===")
                print(json.dumps(stats, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"错误: 保存数据失败 - {e}")
    else:
        print("警告: 没有成功获取任何用户信息")


if __name__ == '__main__':
    main()
