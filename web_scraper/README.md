# 简单网页爬虫程序

这是一个简单易用的网页爬虫程序，可以抓取网页内容并提取有用信息。

## 功能特点

- 🕷️ **简单易用**: 只需输入网址即可开始抓取
- 📄 **内容提取**: 自动提取网页标题、描述、正文内容
- 🔗 **链接提取**: 提取页面中的所有链接
- 🖼️ **图片提取**: 提取页面中的图片信息
- 💾 **结果保存**: 自动保存抓取结果为JSON格式
- ⏱️ **请求控制**: 内置延迟机制，避免请求过于频繁
- 🛡️ **错误处理**: 完善的异常处理机制

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 交互式使用

运行主程序，按提示输入网址：

```bash
python simple_scraper.py
```

### 2. 编程方式使用

```python
from simple_scraper import SimpleWebScraper

# 创建爬虫实例
scraper = SimpleWebScraper(timeout=10, delay=1.0)

# 抓取网页
page_info = scraper.get_page_content("https://example.com")

if page_info:
    print(f"标题: {page_info['title']}")
    print(f"描述: {page_info['description']}")
    print(f"内容: {page_info['content'][:200]}...")
    
    # 保存结果
    scraper.save_results(page_info)
```

### 3. 运行示例

```bash
python example.py
```

## 输出结果

程序会提取以下信息：

- **标题**: 网页标题
- **描述**: 网页描述（从meta标签提取）
- **内容**: 主要文本内容
- **链接**: 页面中的链接列表
- **图片**: 页面中的图片信息
- **状态码**: HTTP响应状态码
- **内容长度**: 页面内容字符数
- **时间戳**: 抓取时间

## 保存格式

结果会保存为JSON格式，包含完整的网页信息：

```json
{
  "url": "https://example.com",
  "title": "网页标题",
  "description": "网页描述",
  "content": "主要文本内容...",
  "links": [
    {
      "text": "链接文本",
      "url": "https://example.com/link"
    }
  ],
  "images": [
    {
      "src": "https://example.com/image.jpg",
      "alt": "图片描述"
    }
  ],
  "status_code": 200,
  "content_length": 1234,
  "timestamp": 1234567890.123
}
```

## 配置选项

创建爬虫实例时可以配置以下参数：

- `timeout`: 请求超时时间（默认10秒）
- `delay`: 请求间隔时间（默认1秒）

```python
scraper = SimpleWebScraper(timeout=15, delay=2.0)
```

## 注意事项

1. **遵守robots.txt**: 请确保遵守目标网站的robots.txt规则
2. **请求频率**: 程序内置延迟机制，避免请求过于频繁
3. **错误处理**: 程序会自动处理网络错误和解析错误
4. **编码支持**: 自动检测和设置正确的字符编码

## 文件结构

```
web_scraper/
├── simple_scraper.py    # 主程序
├── example.py           # 使用示例
├── requirements.txt     # 依赖包
├── README.md           # 说明文档
└── results/            # 结果保存目录
```

## 依赖包

- `requests`: HTTP请求库
- `beautifulsoup4`: HTML解析库
- `lxml`: XML/HTML解析器
- `urllib3`: HTTP客户端库

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和网站使用条款。