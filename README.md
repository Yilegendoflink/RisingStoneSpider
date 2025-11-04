# RisingStoneSpider 石之猪🐖

一个网页爬虫软件，用于根据UID爬取特定论坛的用户个人信息页信息用于统计数据。

## 功能特性

- 🎯 基于UID精准爬取用户个人信息
- 📊 支持批量爬取多个用户数据
- 💾 支持JSON和CSV格式数据导出
- 🔄 智能重试机制和错误处理
- ⚡ 可配置的请求速率限制
- 📝 完整的日志记录
- 📈 数据统计功能

## 安装

### 前置要求

- Python 3.7+
- pip

### 安装步骤

1. 克隆仓库:
```bash
git clone https://github.com/Yilegendoflink/RisingStoneSpider.git
cd RisingStoneSpider
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

## 配置

编辑 `config.json` 文件以配置目标论坛和爬虫行为:

```json
{
  "forum_url": "https://example.com/forum",
  "user_profile_path": "/user/profile/{uid}",
  "output_dir": "data",
  "output_format": "json",
  "rate_limit_seconds": 1,
  "timeout": 10,
  "max_retries": 3,
  "user_agent": "Mozilla/5.0 ..."
}
```

### 配置项说明

- `forum_url`: 论坛基础URL
- `user_profile_path`: 用户个人信息页路径模板（{uid}会被替换为实际UID）
- `output_dir`: 输出数据存储目录
- `output_format`: 输出格式 (json 或 csv)
- `rate_limit_seconds`: 请求间隔时间（秒）
- `timeout`: 请求超时时间（秒）
- `max_retries`: 失败重试次数
- `user_agent`: HTTP请求的User-Agent

## 使用方法

### 基本用法

爬取单个用户信息:
```bash
python main.py --uid 12345
```

爬取多个用户信息:
```bash
python main.py --uid 12345 23456 34567
```

从文件读取UID列表:
```bash
python main.py --uid-file uids.txt
```

### 高级用法

指定输出文件名:
```bash
python main.py --uid 12345 --output my_data
```

使用自定义配置文件:
```bash
python main.py --uid 12345 --config custom_config.json
```

显示统计信息:
```bash
python main.py --uid 12345 23456 --stats
```

### UID文件格式

创建一个文本文件（如 `uids.txt`），每行一个UID:
```
12345
23456
34567
45678
```

## 输出数据格式

### JSON格式示例

```json
[
  {
    "uid": "12345",
    "username": "用户名",
    "posts_count": "100",
    "registration_date": "2023-01-01",
    "last_active": "2024-01-01",
    "reputation": "500",
    "profile_url": "https://example.com/forum/user/profile/12345",
    "fetch_time": "2024-11-04T06:04:00"
  }
]
```

### CSV格式示例

```csv
uid,username,posts_count,registration_date,last_active,reputation,profile_url,fetch_time
12345,用户名,100,2023-01-01,2024-01-01,500,https://example.com/forum/user/profile/12345,2024-11-04T06:04:00
```

## 数据解析自定义

爬虫使用 BeautifulSoup 解析HTML。要适配不同的论坛结构，需要修改 `spider.py` 中的 `_parse_user_profile` 方法，根据目标论坛的实际HTML结构调整CSS选择器。

示例:
```python
def _parse_user_profile(self, html: str, uid: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, 'lxml')
    
    user_info = {
        'uid': uid,
        'username': soup.select_one('.user-name').get_text(strip=True),
        'posts_count': soup.select_one('.post-count').get_text(strip=True),
        # 根据实际HTML结构添加更多字段...
    }
    
    return user_info
```

## 日志

运行日志会保存在 `spider.log` 文件中，包含:
- 爬取进度
- 成功/失败记录
- 错误信息
- 重试记录

## 注意事项

⚠️ **使用须知**:

1. 请遵守目标网站的robots.txt规则
2. 合理设置请求频率，避免对服务器造成压力
3. 仅用于合法的数据分析和研究目的
4. 尊重用户隐私，妥善保管爬取的数据
5. 部分网站可能需要登录认证，需要额外处理Cookie/Token

## 故障排除

### 常见问题

1. **连接超时**: 增加 `config.json` 中的 `timeout` 值
2. **频繁失败**: 降低请求频率，增加 `rate_limit_seconds` 值
3. **解析失败**: 检查并更新 `_parse_user_profile` 方法中的选择器

## 开发

### 项目结构

```
RisingStoneSpider/
├── main.py           # 主程序入口
├── spider.py         # 爬虫核心类
├── config.json       # 配置文件
├── requirements.txt  # Python依赖
├── .gitignore       # Git忽略文件
└── README.md        # 项目文档
```

### 扩展功能

可以通过继承 `ForumSpider` 类来扩展功能:

```python
from spider import ForumSpider

class CustomSpider(ForumSpider):
    def _parse_user_profile(self, html, uid):
        # 自定义解析逻辑
        pass
```

## 依赖库

- `requests`: HTTP请求库
- `beautifulsoup4`: HTML解析库
- `lxml`: XML/HTML解析器

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request！

## 作者

Yilegendoflink

---

**免责声明**: 使用本工具爬取数据时，请确保遵守相关法律法规和网站使用条款。作者不对使用本工具产生的任何后果负责。
