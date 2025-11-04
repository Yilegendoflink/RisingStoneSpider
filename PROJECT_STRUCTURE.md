# 项目结构

```
RisingStoneSpider/
├── .git/                   # Git版本控制文件夹
├── .gitignore             # Git忽略文件配置
├── config.json            # 爬虫配置文件
├── ff14_spider.py         # 主爬虫程序（核心文件）
├── run.py                 # 快速启动脚本
├── requirements.txt       # Python依赖包列表
├── README.md              # 项目说明文档
├── PROJECT_STRUCTURE.md   # 本文件
├── output/                # 输出文件夹
│   ├── spider_results_*.json    # 爬取结果数据
│   ├── screenshot_*.png         # 页面截图
│   └── page_source_*.html       # 页面源码
└── venv/                  # Python虚拟环境（已在.gitignore中）
```

## 核心文件说明

### ff14_spider.py
- 主爬虫程序
- 包含完整的爬虫逻辑
- 支持登录检测和动态内容等待
- 模块化设计，易于维护

### config.json
- 爬虫配置文件
- 可配置浏览器参数、超时时间、CSS选择器等
- 支持自定义目标URL列表

### run.py
- 快速启动脚本
- 提供交互式界面
- 支持自定义URL输入

### output/
- 所有爬取结果自动保存在此文件夹
- 包含JSON数据、截图和页面源码
- 文件名包含时间戳便于管理

## 使用流程

1. 安装依赖：`pip install -r requirements.txt`
2. 运行爬虫：`python run.py` 或 `python ff14_spider.py`
3. 按提示完成登录（如需要）
4. 查看output文件夹中的结果