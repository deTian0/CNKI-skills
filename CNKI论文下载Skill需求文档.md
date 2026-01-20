# CNKI论文批量下载Skill需求文档

## 1. 需求概述

### 1.1 项目目标

开发一个Claude Skill，能够自动化地从中国知网(CNKI)批量下载学术论文，支持多种文献类型，智能识别用户意图，并提供高效的并发下载能力。

### 1.2 核心价值

- **自动化流程**: 从检索到下载全流程自动化
- **智能识别**: 理解自然语言中的文献类型和需求
- **高效下载**: 支持并发下载，提升效率
- **灵活配置**: 支持自定义下载目录和命名规则

---

## 2. 功能需求

### 2.1 用户输入解析

#### 2.1.1 输入格式

支持多种自然语言表达方式，例如：

```
标准格式:
"帮我下载5篇跟'人工智能'相关的学位论文到 D:\papers\"

变体格式:
- "下载10篇关于机器学习的期刊文章到 C:\docs\"
- "帮我下20个会议论文，主题是深度学习，保存到 ~/papers/"
- "下载5篇专利，关键词是区块链，到 D:\patents\"
```

#### 2.1.2 必需参数识别

| 参数       | 说明     | 示例                     | 是否必需       |
|----------|--------|------------------------|------------|
| **关键词**  | 检索关键词  | "人工智能"、"机器学习"          | ✅ 必需       |
| **数量**   | 下载论文数量 | "5篇"、"10个"             | ✅ 必需       |
| **文献类型** | 文献类型   | "学位论文"、"期刊"            | ✅ 必需（有默认值） |
| **保存目录** | 下载保存路径 | "D:\papers\"、"~/docs/" | ✅ 必需       |

#### 2.1.3 文献类型映射表

**10种标准类型映射规则:**

| 用户输入 | 映射类型   | 别名/变体                                 |
|------|--------|---------------------------------------|
| 学术期刊 | `学术期刊` | 期刊、期刊文章、期刊论文、magazine、journal         |
| 学位论文 | `学位论文` | 学位、硕博论文、硕士论文、博士论文、thesis、dissertation |
| 会议   | `会议`   | 会议论文、会议文章、conference、proceedings      |
| 报纸   | `报纸`   | 报纸文章、newspaper                        |
| 年鉴   | `年鉴`   | 统计年鉴、yearbook、almanac                 |
| 专利   | `专利`   | patent、专利文献                           |
| 标准   | `标准`   | standard、标准文献、规范                      |
| 成果   | `成果`   | 科技成果、achievements、成果                  |
| 学术辑刊 | `学术辑刊` | 辑刊                                    |
| 图书   | `图书`   | 图书章节、book、图书文献                        |
| 文库   | `文库`   | 知网文库、wenku                            |

**默认值**: 如果用户未指定文献类型，默认使用"学术期刊"

### 2.2 核心功能流程

#### 2.2.1 主流程

```
┌─────────────────────────────────────┐
│  1. 解析用户输入                     │
│     - 提取关键词、数量、类型、目录    │
├─────────────────────────────────────┤
│  2. 初始化浏览器                     │
│     - 启动Playwright                 │
│     - 设置下载路径                   │
├─────────────────────────────────────┤
│  3. 导航到CNKI首页                   │
│     - 访问 https://www.cnki.net/     │
│     - 等待页面加载完成               │
├─────────────────────────────────────┤
│  4. 选择文献类型                     │
│     - 在首页找到10种文献类型导航     │
│     - 点击对应的文献类型链接         │
│     - 等待进入文献类型库页面         │
├─────────────────────────────────────┤
│  5. 执行检索                         │
│     - 定位搜索框                     │
│     - 输入关键词                     │
│     - 点击"检索"按钮                 │
│     - 等待结果页加载                 │
├─────────────────────────────────────┤
│  6. 获取论文列表                     │
│     - 提取前N篇论文的基本信息         │
│     - 包含: 标题、作者、来源、年份    │
├─────────────────────────────────────┤
│  7. 并发下载                         │
│     - 同时启动多个下载任务            │
│     - 每个任务处理一篇论文            │
│     - 保存到指定目录                 │
├─────────────────────────────────────┤
│  8. 生成报告                         │
│     - 统计成功/失败数量              │
│     - 列出下载文件列表               │
│     - 记录跳过的论文及原因            │
└─────────────────────────────────────┘
```

#### 2.2.2 页面操作细节

**步骤1: 导航到首页**

```
URL: https://www.cnki.net/
等待: 页面完全加载（判断标准: 搜索框可见）
```

**步骤2: 选择文献类型**

```
定位方式: 基于页面快照中的文献类型导航区
选择器策略:
  - 方法A: 通过链接文本定位（推荐）
    例: page.get_by_role("link", name="学位论文")

  - 方法B: 通过CSS选择器
    根据classid参数识别

操作: 点击链接
等待: 文献类型库页面加载（判断: 搜索框出现）
```

**步骤3: 执行检索**

```
搜索框定位:
  - 选择器: textbox[placeholder*="文献"]
  - 或: input[type="text"][class*="search"]

输入操作:
  - 清空现有内容
  - 输入关键词（支持中文）

检索按钮:
  - 定位: button[type="submit"] 或包含"检索"文本的按钮

等待: 结果页加载完成（判断: 结果列表出现）
```

**步骤4: 获取论文列表**

```
结果列表容器定位:
  - 选择器: .result-table-list 或 .grid-list
  - 或: 包含论文条目的列表容器

每个论文条目包含:
  - 标题（必需）: 用于文件命名
  - 作者（可选）: 用于显示
  - 来源（可选）: 期刊/学位授予单位
  - 年份（可选）: 用于排序/筛选
  - 下载按钮（必需）: PDF下载链接

提取前N篇:
  - 如果一页不足N篇，需要翻页
  - 翻页逻辑: 点击"下一页"或直接跳转到指定页
```

**步骤5: 下载单篇论文**

```
定位下载按钮:
  - 优先: "PDF下载"按钮
  - 备选: "CAJ下载"按钮
  - 选择器:
    - a:has-text("PDF下载")
    - 或: a:has-text("下载")
    - 或: button:has-text("下载")

处理下载:
  - 点击下载按钮
  - 浏览器会处理文件下载
  - 文件保存到指定目录

异常处理:
  - 如果遇到付费页面: 跳过，记录原因
  - 如果下载失败: 重试1次，仍失败则跳过
  - 如果文件名冲突: 添加序号后缀
```

### 2.3 文件命名规则

#### 2.3.1 命名格式

```
格式: {标题}.pdf

规则:
1. 使用论文原标题
2. 移除文件名中的非法字符
3. 限制长度（避免超过系统限制）
4. 处理同名文件（添加序号）

示例:
原文: 智能赋影，融合创新：人工智能时代下医学影像学科的发展与展望
文件名: 智能赋影，融合创新：人工智能时代下医学影像学科的发展与展望.pdf

清理后: 智能赋影_融合创新_人工智能时代下医学影像学科的发展与展望.pdf
（替换特殊字符为下划线）
```

#### 2.3.2 文件名清理规则

```
非法字符替换:
  - \ / : * ? " < > | → _
  - 全角符号 → 半角符号
  - 多个空格 → 单个下划线

长度限制:
  - Windows: 255字符
  - 建议: 限制在200字符以内
  - 超长处理: 截断并添加"..."

示例:
"人工智能在医疗影像中的应用：现状与展望（2023）"
↓
"人工智能在医疗影像中的应用_现状与展望_2023_.pdf"
```

### 2.4 并发下载策略

#### 2.4.1 并发控制

```
并发数: 3个同时下载任务

理由:
- 避免过多并发导致服务器限制
- 平衡下载速度和稳定性
- 降低被封禁IP的风险

实现方式:
- 使用任务队列
- 信号量控制并发数
- 失败任务自动重试
```

#### 2.4.2 下载队列管理

```
队列结构:
  待下载队列 → 下载中 → 完成/失败

处理流程:
  1. 将N篇论文加入待下载队列
  2. 同时启动3个下载worker
  3. 每个worker从队列取任务
  4. 完成后处理下一篇
  5. 所有任务完成后生成报告

状态跟踪:
  - 已下载: X/N
  - 下载中: Y个
  - 待下载: Z个
  - 失败/跳过: W个
```

### 2.5 异常处理机制

#### 2.5.1 页面加载超时

```
场景: 页面加载缓慢或卡住
处理:
  - 设置超时时间（默认30秒）
  - 超时后刷新页面重试
  - 3次重试失败则报错

用户提示:
  "页面加载超时，正在重试..."
```

#### 2.5.2 元素定位失败

```
场景: 找不到搜索框、按钮等元素
处理:
  - 尝试备用选择器
  - 等待2秒后重试
  - 记录错误日志

用户提示:
  "无法定位[元素名称]，页面结构可能已变化"
```

#### 2.5.3 下载失败

```
场景: 点击下载后文件未保存
原因:
  - 网络中断
  - 服务器返回错误
  - 磁盘空间不足
  - 权限不足

处理:
  - 记录失败论文信息
  - 继续下载下一篇
  - 最后统一报告

用户提示:
  "论文《标题》下载失败，已跳过"
```

#### 2.5.4 付费论文

```
场景: 提示需要购买或权限不足
处理:
  - 跳过该论文
  - 记录原因: "需要付费"
  - 继续下载其他论文

用户提示:
  "论文《标题》需要付费权限，已跳过"
```

#### 2.5.5 文件系统错误

```
场景: 目录不存在、权限不足
处理:
  - 尝试创建目录（如果不存在）
  - 检查写入权限
  - 失败则终止下载并提示

用户提示:
  "无法写入目录 {path}，请检查权限"
```

---

## 3. 技术实现方案

### 3.1 技术栈

#### 3.1.1 核心技术

- **Playwright**: 浏览器自动化
    - 已在Claude Code环境中集成
    - 支持Chromium内核
    - 提供稳定的API

- **Python 3.x**: 主要开发语言
    - 异步编程支持
    - 丰富的库生态

- **正则表达式**: 用户输入解析
- **pathlib**: 路径处理
- **asyncio**: 并发控制

#### 3.1.2 项目结构

```
cnki-downloader-skill/
├── skill.json                 # Skill配置文件
├── README.md                  # 使用说明
├── src/
│   ├── __init__.py
│   ├── main.py               # 主入口
│   ├── config.py             # 配置管理
│   ├── parser.py             # 用户输入解析
│   ├── cnki_browser.py       # CNKI浏览器操作
│   ├── downloader.py         # 下载器
│   ├── models.py             # 数据模型
│   └── utils.py              # 工具函数
├── tests/
│   ├── test_parser.py        # 解析器测试
│   └── test_downloader.py    # 下载器测试
└── docs/
    ├── API.md                # API文档
    └── workflow.md           # 流程说明
```

### 3.2 核心模块设计

#### 3.2.1 用户输入解析器

**功能**: 从自然语言中提取结构化参数

```python
class InputParser:
    """解析用户输入"""

    def parse(self, text: str) -> DownloadRequest:
        """
        解析输入文本

        返回:
            DownloadRequest {
                keyword: str,          # 关键词
                count: int,            # 数量
                doc_type: str,         # 文献类型
                save_dir: Path,        # 保存目录
            }
        """

    def _extract_keyword(self, text: str) -> str:
        """提取关键词（支持引号、空格等）"""

    def _extract_count(self, text: str) -> int:
        """提取数量（支持"5篇"、"十个"等）"""

    def _extract_doc_type(self, text: str) -> str:
        """提取并映射文献类型"""

    def _extract_save_dir(self, text: str) -> Path:
        """提取保存目录（支持~、相对路径等）"""
```

#### 3.2.2 CNKI浏览器操作

**功能**: 封装所有CNKI页面操作

```python
class CNKIBrowser:
    """CNKI浏览器操作封装"""

    def __init__(self, download_dir: Path):
        self.browser = playwright.chromium.launch()
        self.context = self.browser.new_context()
        # 设置下载目录
        self.context.set_download_path(download_dir)

    async def goto_homepage(self) -> Page:
        """导航到CNKI首页"""

    async def select_document_type(self, doc_type: str) -> Page:
        """选择文献类型"""
        # 策略1: 通过链接文本定位
        # 策略2: 通过选择器定位

    async def search(self, keyword: str) -> Page:
        """执行检索"""

    async def get_paper_list(self, count: int) -> List[Paper]:
        """获取论文列表"""
        # 处理分页
        # 提取论文信息

    async def download_paper(self, paper: Paper) -> DownloadResult:
        """下载单篇论文"""

    async def close(self):
        """关闭浏览器"""
```

#### 3.2.3 并发下载器

**功能**: 管理并发下载任务

```python
class ConcurrentDownloader:
    """并发下载器"""

    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def download_all(
            self,
            papers: List[Paper],
            browser: CNKIBrowser
    ) -> List[DownloadResult]:
        """并发下载所有论文"""

        tasks = [
            self._download_single(paper, browser)
            for paper in papers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def _download_single(
            self,
            paper: Paper,
            browser: CNKIBrowser
    ) -> DownloadResult:
        """下载单篇（带并发控制）"""

        async with self.semaphore:
            # 执行下载
            result = await browser.download_paper(paper)
            return result
```

### 3.3 选择器策略

基于之前页面视图分析，定义关键元素的选择器：

#### 3.3.1 首页文献类型导航

```python
DOCUMENT_TYPE_SELECTORS = {
    "学术期刊": "a:has-text('学术期刊')",
    "学位论文": "a:has-text('学位论文')",
    "会议": "a:has-text('会议')",
    "报纸": "a:has-text('报纸')",
    "年鉴": "a:has-text('年鉴')",
    "专利": "a:has-text('专利')",
    "标准": "a:has-text('标准')",
    "成果": "a:has-text('成果')",
    "学术辑刊": "a:has-text('学术辑刊')",
    "图书": "a:has-text('图书')",
    "文库": "a:has-text('文库')",
}

# 备用选择器（基于href属性）
FALLBACK_SELECTORS = {
    "学位论文": "a[href*='rt=dissertation']",
    "学术期刊": "a[href*='rt=journal']",
    # ...
}
```

#### 3.3.2 检索框

```python
SEARCH_INPUT_SELECTORS = [
    "input[placeholder*='文献']",
    "input[type='text'].search-input",
    "input[class*='search']",
    "#search-input",
]
```

#### 3.3.3 检索按钮

```python
SEARCH_BUTTON_SELECTORS = [
    "button:has-text('检索')",
    "input[type='submit'][value*='检索']",
    ".search-btn",
]
```

#### 3.3.4 论文列表项

```python
PAPER_ITEM_SELECTOR = ".result-table-list tr"
# 或
PAPER_ITEM_SELECTOR = ".grid-list-item"

# 提取信息
TITLE_SELECTOR = ".title a"
AUTHOR_SELECTOR = ".author"
SOURCE_SELECTOR = ".source"
YEAR_SELECTOR = ".date"

# 下载按钮
PDF_DOWNLOAD_SELECTOR = "a:has-text('PDF下载')"
CAJ_DOWNLOAD_SELECTOR = "a:has-text('CAJ下载')"
```

### 3.4 配置管理

#### 3.4.1 默认配置

```python
# config.py
DEFAULT_CONFIG = {
    # 下载设置
    "download_dir": Path("~/Downloads/CNKI").expanduser(),
    "max_concurrent": 3,
    "timeout": 30000,  # 30秒
    "retry_times": 2,

    # 浏览器设置
    "headless": False,  # 是否无头模式
    "slow_mo": 100,  # 操作延迟（毫秒）

    # 文件命名
    "sanitize_filename": True,
    "max_filename_length": 200,
    "conflict_strategy": "append_number",  # 或 "skip", "overwrite"

    # 默认值
    "default_doc_type": "学术期刊",
    "default_count": 10,
}
```

#### 3.4.2 用户配置文件

```json
// config.json (用户可选)
{
  "download_dir": "D:\\papers\\",
  "max_concurrent": 5,
  "headless": true,
  "default_doc_type": "学位论文"
}
```

---

## 4. 用户交互设计

### 4.1 命令格式

#### 4.1.1 标准命令

```
下载 {数量} 篇关于 "{关键词}" 的 {文献类型} 到 {目录}
```

#### 4.1.2 简化命令

```
下载 {数量} 篇 {关键词} {文献类型} {目录}
```

#### 4.1.3 实际示例

```
✅ 正确示例:
"帮我下载5篇跟'人工智能'相关的学位论文到 D:\papers\"
"下载10篇关于机器学习的期刊文章到 C:\docs\"
"帮我下20个会议论文，主题是深度学习，保存到 ~/papers/"
"下载5篇专利，关键词是区块链，到 D:\patents\"

❌ 错误示例:
"下载一些论文"  # 缺少数量和关键词
"下载5篇论文"   # 缺少关键词
"下载论文"     # 信息不足
```

### 4.2 输出报告格式

#### 4.2.1 成功报告

```
✅ 下载完成！

📊 下载统计:
   总计: 5篇
   成功: 5篇
   跳过: 0篇

📁 保存位置: D:\papers\

📄 下载文件列表:
   ✅ 智能赋影，融合创新：人工智能时代下医学影像学科的发展与展望.pdf
   ✅ 人工智能在医疗诊断中的应用研究.pdf
   ✅ 基于深度学习的医学影像分析技术综述.pdf
   ✅ AI辅助诊断系统的临床应用与挑战.pdf
   ✅ 人工智能时代医学教育的变革与创新.pdf

⏱️  耗时: 2分15秒
🚀 平均速度: 2.2篇/分钟
```

#### 4.2.2 部分成功报告

```
⚠️ 下载完成（部分成功）

📊 下载统计:
   总计: 10篇
   成功: 8篇
   跳过: 2篇

📁 保存位置: D:\papers\

📄 成功下载 (8篇):
   ✅ 论文标题1.pdf
   ✅ 论文标题2.pdf
   ...

⚠️ 跳过论文 (2篇):
   ⚠️ 论文标题A.pdf - 原因: 需要付费权限
   ⚠️ 论文标题B.pdf - 原因: 下载失败（网络错误）

💡 建议: 检查跳过的论文，可能需要登录或稍后重试

⏱️  耗时: 3分42秒
```

#### 4.2.3 失败报告

```
❌ 下载失败

错误原因: 无法定位搜索框

💡 可能的原因:
   1. 页面加载超时
   2. 网络连接问题
   3. CNKI页面结构已变化

🔧 故障排除:
   1. 检查网络连接
   2. 尝试手动访问 https://www.cnki.net/
   3. 稍后重试

📍 已保存错误日志: D:\papers\download_error_20250107.log
```

### 4.3 进度提示（可选）

在下载过程中提供实时进度：

```
正在下载论文...

[████████░░░░░░░░░░] 40% (2/5)

当前任务: 正在下载第3篇...
   标题: 基于深度学习的医学影像分析技术综述.pdf
   进度: ████████░░ 80%
   速度: 1.2 MB/s

预计剩余时间: 45秒
```

---

## 5. 测试用例

### 5.1 功能测试

#### 5.1.1 输入解析测试

```python
def test_parse_standard_input():
    """测试标准输入解析"""
    text = "帮我下载5篇跟'人工智能'相关的学位论文到 D:\\papers\\"
    request = parser.parse(text)

    assert request.keyword == "人工智能"
    assert request.count == 5
    assert request.doc_type == "学位论文"
    assert request.save_dir == Path("D:\\papers\\")


def test_parse_with_aliases():
    """测试别名识别"""
    test_cases = [
        ("下载5篇硕博论文", "学位论文"),
        ("下载10篇期刊文章", "学术期刊"),
        ("下载3个会议论文", "会议"),
        ("下2个patent", "专利"),
    ]

    for text, expected_type in test_cases:
        request = parser.parse(text)
        assert request.doc_type == expected_type


def test_parse_without_doc_type():
    """测试未指定文献类型"""
    text = "下载5篇关于AI的论文到 D:\\papers\\"
    request = parser.parse(text)

    assert request.doc_type == "学术期刊"  # 默认值


def test_parse_chinese_numbers():
    """测试中文数字"""
    test_cases = [
        ("下载五篇", 5),
        ("下载十篇", 10),
        ("下载二十篇", 20),
        ("下载100篇", 100),
    ]

    for text, expected_count in test_cases:
        # 需要包含其他必需参数
        full_text = f"{text}论文到 D:\\papers\\"
        request = parser.parse(full_text)
        assert request.count == expected_count
```

#### 5.1.2 下载流程测试

```python
async def test_full_download_flow():
    """测试完整下载流程"""
    # 1. 创建下载器
    downloader = CNKIDownloader()

    # 2. 执行下载
    request = DownloadRequest(
        keyword="人工智能",
        count=3,
        doc_type="学位论文",
        save_dir=Path("D:\\test\\")
    )

    result = await downloader.download(request)

    # 3. 验证结果
    assert result.total == 3
    assert result.success_count >= 0
    assert len(result.files) == result.success_count
    assert result.save_dir.exists()


async def test_concurrent_download():
    """测试并发下载"""
    downloader = CNKIDownloader(max_concurrent=3)

    request = DownloadRequest(
        keyword="机器学习",
        count=10,
        doc_type="学术期刊",
        save_dir=Path("D:\\test\\")
    )

    start_time = time.time()
    result = await downloader.download(request)
    elapsed_time = time.time() - start_time

    # 并发下载应该比串行快
    # 假设平均每篇30秒，10篇串行需要300秒
    # 3并发应该约100-120秒
    assert elapsed_time < 200  # 留些余量


async def test_error_handling():
    """测试错误处理"""
    downloader = CNKIDownloader()

    # 模拟网络错误
    with mock.patch.object(downloader, '_download_single',
                           side_effect=NetworkError):
        result = await downloader.download(
            DownloadRequest(
                keyword="test",
                count=5,
                doc_type="学术期刊",
                save_dir=Path("D:\\test\\")
            )
        )

        assert result.total == 5
        assert result.success_count == 0
        assert result.skip_count == 5
```

#### 5.1.3 文件命名测试

```python
def test_filename_sanitization():
    """测试文件名清理"""
    test_cases = [
        (
            "人工智能/医学影像：应用与展望",
            "人工智能_医学影像_应用与展望.pdf"
        ),
        (
            "AI、ML、DL在医疗领域的应用**",
            "AI_ML_DL在医疗领域的应用__.pdf"
        ),
        (
            "A" * 300,  # 超长标题
            "A" * 197 + "....pdf"
        ),
    ]

    for original, expected in test_cases:
        result = sanitize_filename(original)
        assert result == expected


def test_duplicate_filename_handling():
    """测试重名处理"""
    # 模拟已存在文件
    existing_files = [
        Path("D:\\test\\论文.pdf"),
    ]

    new_filename = generate_unique_filename(
        "论文.pdf",
        existing_files
    )

    assert new_filename == "论文_1.pdf"
```

### 5.2 边界测试

```python
async def test_large_count():
    """测试大量下载"""
    request = DownloadRequest(
        keyword="人工智能",
        count=100,  # 大数量
        doc_type="学术期刊",
        save_dir=Path("D:\\test\\")
    )

    result = await downloader.download(request)
    assert result.success_count <= 100


async def test_special_keyword():
    """测试特殊关键词"""
    test_keywords = [
        "人工智能+医疗",  # 包含特殊字符
        "AI/Machine Learning",  # 包含斜杠
        "数据科学与大数据",  # 较长
        "",  # 空字符串（应报错）
    ]

    for keyword in test_keywords:
        if keyword:  # 非空
            request = DownloadRequest(
                keyword=keyword,
                count=1,
                doc_type="学术期刊",
                save_dir=Path("D:\\test\\")
            )
            result = await downloader.download(request)
            assert result.total == 1
        else:  # 空字符串
            with pytest.raises(ValueError):
                parser.parse(f"下载5篇到 D:\\test\\")


async def test_invalid_directory():
    """测试无效目录"""
    request = DownloadRequest(
        keyword="test",
        count=1,
        doc_type="学术期刊",
        save_dir=Path("Z:\\nonexistent\\")  # 不存在的路径
    )

    with pytest.raises(DirectoryNotFoundError):
        await downloader.download(request)
```

### 5.3 性能测试

```python
async def test_download_speed():
    """测试下载速度"""
    request = DownloadRequest(
        keyword="人工智能",
        count=10,
        doc_type="学位论文",
        save_dir=Path("D:\\test\\")
    )

    start_time = time.time()
    result = await downloader.download(request)
    elapsed_time = time.time() - start_time

    speed = result.success_count / elapsed_time * 60  # 篇/分钟
    assert speed >= 1.0  # 至少1篇/分钟


async def test_memory_usage():
    """测试内存使用"""
    import tracemalloc

    tracemalloc.start()

    request = DownloadRequest(
        keyword="人工智能",
        count=20,
        doc_type="学术期刊",
        save_dir=Path("D:\\test\\")
    )

    await downloader.download(request)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 内存使用不应超过500MB
    assert peak < 500 * 1024 * 1024
```

---

## 6. 部署与使用

### 6.1 安装步骤

```bash
# 1. 安装Skill
cp -r cnki-downloader-skill ~/.claude/skills/

# 2. 安装依赖（如果需要）
pip install playwright
playwright install chromium

# 3. 重启Claude Code
```

### 6.2 使用示例

#### 6.2.1 基础使用

```
用户: 帮我下载5篇跟"人工智能"相关的学位论文到 D:\papers\

Claude: 好的，我来帮您下载论文。

🔍 正在解析输入...
   关键词: 人工智能
   文献类型: 学位论文
   数量: 5篇
   保存目录: D:\papers\

🌐 正在打开CNKI...
✓ 已访问首页

📚 正在选择文献类型...
✓ 已选择"学位论文"

🔎 正在执行检索...
✓ 已检索"人工智能"

📥 正在下载论文...
   [████████░░░░░░░░░░] 40% (2/5)
   ✅ 智能赋影，融合创新.pdf
   ✅ 人工智能在医疗诊断中的应用.pdf
   ⏳ 正在下载第3篇...

✅ 下载完成！

📊 下载统计:
   总计: 5篇
   成功: 5篇
   跳过: 0篇

📁 保存位置: D:\papers\
```

#### 6.2.2 高级使用

```
用户: 下载10篇关于"区块链+隐私保护"的会议论文到 C:\BlockchainPapers\

Claude: 好的，我来帮您下载。

🔍 正在解析输入...
   关键词: 区块链+隐私保护
   文献类型: 会议
   数量: 10篇
   保存目录: C:\BlockchainPapers\

🌐 正在打开CNKI...
...

✅ 下载完成！

📊 下载统计:
   总计: 10篇
   成功: 9篇
   跳过: 1篇

📄 成功下载 (9篇):
   ✅ 基于区块链的隐私保护方案研究.pdf
   ...

⚠️ 跳过论文 (1篇):
   ⚠️ 区块链隐私计算综述.pdf - 原因: 需要付费权限
```

### 6.3 故障排除

#### 6.3.1 常见问题

**Q: 下载速度很慢怎么办？**
A:

- 检查网络连接
- 减少并发数（改为2）
- 避开高峰时段

**Q: 提示"无法定位搜索框"？**
A:

- 检查CNKI是否可访问
- 尝试手动访问 https://www.cnki.net/
- 查看错误日志

**Q: 部分论文下载失败？**
A:

- 检查是否需要登录
- 确认账号权限
- 查看跳过原因

**Q: 文件名乱码？**
A:

- 确保使用UTF-8编码
- 检查系统语言设置

---

## 7. 后续优化方向

### 7.1 功能增强

- [ ] **智能筛选**: 支持按年份、影响因子筛选
- [ ] **断点续传**: 记录下载进度，支持中断恢复
- [ ] **批量任务**: 支持一次提交多个下载任务
- [ ] **代理支持**: 支持配置代理服务器
- [ ] **OCR识别**: 支持扫描版论文的文字提取

### 7.2 用户体验优化

- [ ] **图形界面**: 提供GUI界面（可选）
- [ ] **进度条**: 实时显示下载进度
- [ ] **预览功能**: 下载前预览论文摘要
- [ ] **去重功能**: 自动跳过已下载的论文

### 7.3 性能优化

- [ ] **智能限速**: 根据服务器响应自动调整并发数
- [ ] **缓存机制**: 缓存检索结果，避免重复检索
- [ ] **增量下载**: 只下载新增论文

---

## 8. 附录

### 8.1 文献类型完整映射表

| 标准名称 | 别名列表                                     | 优先级 |
|------|------------------------------------------|-----|
| 学术期刊 | 期刊,期刊文章,期刊论文,journal,magazine,核心期刊,CSSCI | 1   |
| 学位论文 | 学位,硕博论文,硕士论文,博士论文,thesis,dissertation    | 2   |
| 会议   | 会议,会议论文,会议文章,conference,proceedings,学术会议 | 3   |
| 报纸   | 报纸,报纸文章,newspaper,报刊                     | 4   |
| 年鉴   | 年鉴,统计年鉴,yearbook,almanac                 | 5   |
| 专利   | 专利,patent,专利文献,发明专利                      | 6   |
| 标准   | 标准,standard,标准文献,规范,行业标准                 | 7   |
| 成果   | 成果,科技成果,achievements,科技成果                | 8   |
| 学术辑刊 | 辑刊,学术辑刊                                  | 9   |
| 图书   | 图书,图书章节,book,图书文献                        | 10  |
| 文库   | 文库,知网文库,wenki                            | 11  |

### 8.2 错误代码表

| 代码   | 说明       | 处理建议      |
|------|----------|-----------|
| E001 | 无法解析用户输入 | 检查输入格式    |
| E002 | 网络连接失败   | 检查网络连接    |
| E003 | 页面加载超时   | 刷新重试      |
| E004 | 无法定位元素   | 检查页面结构    |
| E005 | 下载失败     | 重试或跳过     |
| E006 | 权限不足     | 登录账号      |
| E007 | 磁盘空间不足   | 清理磁盘空间    |
| E008 | 目录权限不足   | 检查目录权限    |
| E009 | 文件名冲突    | 自动处理或询问用户 |
| E010 | 并发超限     | 降低并发数     |

### 8.3 配置文件完整示例

```json
{
  "download_settings": {
    "default_dir": "D:\\Downloads\\Papers",
    "max_concurrent": 3,
    "timeout": 30000,
    "retry_times": 2,
    "chunk_size": 1024
  },
  "browser_settings": {
    "headless": false,
    "slow_mo": 100,
    "user_agent": "Mozilla/5.0...",
    "viewport": {
      "width": 1920,
      "height": 1080
    }
  },
  "file_settings": {
    "sanitize_filename": true,
    "max_filename_length": 200,
    "conflict_strategy": "append_number",
    "encoding": "utf-8"
  },
  "default_values": {
    "doc_type": "学术期刊",
    "count": 10,
    "language": "CHS"
  },
  "logging": {
    "enabled": true,
    "level": "INFO",
    "log_dir": "D:\\Logs\\CNKI",
    "max_log_size": 10485760
  }
}
```

---

## 9. 总结

本需求文档详细描述了CNKI论文批量下载Skill的完整设计方案，包括：

✅ **核心功能**: 用户输入解析、文献类型识别、自动检索、并发下载
✅ **技术方案**: 基于Playwright的浏览器自动化
✅ **异常处理**: 完善的错误处理和恢复机制
✅ **用户体验**: 清晰的进度提示和结果报告
✅ **可扩展性**: 模块化设计，便于后续优化

**关键特性**:

- 🎯 智能识别10种文献类型
- 🚀 并发下载（3个任务同时进行）
- 📁 自动文件命名和冲突处理
- ⚠️ 完善的异常处理机制
- 📊 详细的下载报告

**开发优先级**:

1. 核心下载功能（MVP）
2. 用户输入解析
3. 并发下载优化
4. 异常处理完善
5. 用户体验优化

---

**文档版本**: v1.0
**创建日期**: 2025-01-07
**最后更新**: 2025-01-07
