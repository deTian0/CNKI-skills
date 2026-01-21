# 配置指南

本项目使用 Pydantic v2 和 `.env` 文件管理配置。

## 创建 .env 文件

在项目根目录创建 `.env` 文件，内容如下：

```env
# CNKI论文下载器配置文件

# 下载设置
DOWNLOAD_DEFAULT_DIR=~/Downloads/CNKI
DOWNLOAD_MAX_CONCURRENT=1
DOWNLOAD_TIMEOUT=30000
DOWNLOAD_RETRY_TIMES=2
DOWNLOAD_CHUNK_SIZE=1024

# 浏览器设置
BROWSER_HEADLESS=false
BROWSER_SLOW_MO=500
BROWSER_VIEWPORT_WIDTH=1366
BROWSER_VIEWPORT_HEIGHT=768
BROWSER_LOCALE=zh-CN
BROWSER_TIMEZONE=Asia/Shanghai
BROWSER_USER_AGENT=

# 文件设置
FILE_SANITIZE_FILENAME=true
FILE_MAX_FILENAME_LENGTH=200
FILE_CONFLICT_STRATEGY=append_number
FILE_ENCODING=utf-8

# 默认值
DEFAULT_DOC_TYPE=学术期刊
DEFAULT_COUNT=10
DEFAULT_LANGUAGE=CHS
DEFAULT_UNIPLATFORM=NZKPT

# 日志设置
LOGGING_ENABLED=true
LOGGING_LEVEL=INFO
LOGGING_LOG_DIR=~/cnki_downloader_logs
LOGGING_MAX_LOG_SIZE=10485760
```

## 配置说明

### 下载设置
- `DOWNLOAD_DEFAULT_DIR`: 默认下载目录（支持 `~` 表示用户目录）
- `DOWNLOAD_MAX_CONCURRENT`: 最大并发下载数（建议设为1，避免CNKI限流）
- `DOWNLOAD_TIMEOUT`: 下载超时时间（毫秒）
- `DOWNLOAD_RETRY_TIMES`: 失败重试次数
- `DOWNLOAD_CHUNK_SIZE`: 下载分块大小（字节）

### 浏览器设置
- `BROWSER_HEADLESS`: 是否使用无头模式（true/false）
- `BROWSER_SLOW_MO`: 操作延迟（毫秒），模拟真实用户操作
- `BROWSER_VIEWPORT_WIDTH`: 浏览器视口宽度
- `BROWSER_VIEWPORT_HEIGHT`: 浏览器视口高度
- `BROWSER_LOCALE`: 语言设置
- `BROWSER_TIMEZONE`: 时区设置
- `BROWSER_USER_AGENT`: 自定义用户代理（留空使用默认）

### 浏览器超时设置（毫秒）
- `BROWSER_PAGE_LOAD_TIMEOUT`: 页面加载超时时间（默认15000）
- `BROWSER_NETWORK_IDLE_TIMEOUT`: 网络空闲超时时间（默认10000）
- `BROWSER_SELECTOR_TIMEOUT`: 选择器查找超时时间（默认8000）
- `BROWSER_SELECTOR_RETRY_TIMEOUT`: 选择器重试超时时间（默认10000）
- `BROWSER_DOWNLOAD_BUTTON_TIMEOUT`: 下载按钮查找超时时间（默认3000）
- `BROWSER_ELEMENT_FIND_TIMEOUT`: 元素查找超时时间（默认5000）

### 浏览器等待时间设置（秒）
- `BROWSER_PAGE_SWITCH_WAIT_TIME`: 页面切换等待时间（默认2）
- `BROWSER_SCROLL_WAIT_TIME`: 滚动后等待时间（默认1）
- `BROWSER_CONTENT_LOAD_WAIT_TIME`: 内容加载等待时间（默认2）

### 文件设置
- `FILE_SANITIZE_FILENAME`: 是否清理文件名中的非法字符
- `FILE_MAX_FILENAME_LENGTH`: 最大文件名长度
- `FILE_CONFLICT_STRATEGY`: 文件名冲突处理策略（append_number/skip/overwrite）
- `FILE_ENCODING`: 文件编码

### 默认值
- `DEFAULT_DOC_TYPE`: 默认文献类型
- `DEFAULT_COUNT`: 默认下载数量
- `DEFAULT_LANGUAGE`: 默认语言
- `DEFAULT_UNIPLATFORM`: 平台标识

### 日志设置
- `LOGGING_ENABLED`: 是否启用日志
- `LOGGING_LEVEL`: 日志级别（DEBUG/INFO/WARNING/ERROR）
- `LOGGING_LOG_DIR`: 日志目录（支持 `~` 表示用户目录）
- `LOGGING_MAX_LOG_SIZE`: 最大日志文件大小（字节）

## 配置优先级

1. 环境变量（最高优先级）
2. `.env` 文件
3. JSON 配置文件（`~/.cnki_downloader/config.json`，向后兼容）
4. 默认值（最低优先级）

## 使用示例

```python
from src.config import ConfigManager

# 创建配置管理器（自动加载 .env 文件）
manager = ConfigManager()

# 获取配置
config = manager.get()

# 使用配置
print(f"并发数: {config.download.max_concurrent}")
print(f"无头模式: {config.browser.headless}")
print(f"默认目录: {config.download.default_dir}")
```

## 注意事项

- `.env` 文件不会被提交到 Git（已在 `.gitignore` 中）
- 布尔值使用 `true`/`false`（小写）
- 路径支持 `~` 表示用户目录
- 如果 `.env` 文件不存在，将使用默认配置
