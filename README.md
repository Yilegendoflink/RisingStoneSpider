# FF14 Rising Stones 爬虫

## 功能说明

这是一个专门用于爬取《最终幻想14》官方社区（石之家）玩家个人信息的Selenium爬虫。

## 文件说明

- `ff14_spider.py` - 主爬虫程序
- `config.json` - 配置文件
- `spider_simple.py` - 简化版本（用于测试）
- `spider_with_login.py` - 包含手动登录功能的版本

## 安装依赖

```bash
pip install selenium
```

## 使用方法

1. 运行爬虫：
```bash
python ff14_spider.py
```

2. 浏览器会自动打开并导航到目标页面
3. 如需登录，按提示在浏览器中手动完成登录
4. 爬虫会自动提取玩家信息并保存结果

## 输出文件

- `spider_results_时间戳.json` - 爬取的结构化数据
- `screenshot_时间戳.png` - 页面截图
- `page_source_时间戳.html` - 页面源码

## 配置说明

可以修改 `config.json` 来调整：
- 浏览器设置（是否无头模式等）
- 超时时间
- CSS选择器
- 目标URL列表

## 特性

- 自动检测登录需求
- 反爬虫检测处理
- 支持动态内容等待
- 结构化数据提取
- 自动保存截图和源码
- 模块化设计，易于扩展