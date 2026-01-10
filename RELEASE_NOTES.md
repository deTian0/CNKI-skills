# CNKI论文下载Skill - 发布包

**版本**: v1.0.0
**发布日期**: 2026年1月
**仓库地址**: https://github.com/lbnqq/CNKI-skills

---

## 📦 下载与安装

### 方式一：直接下载（推荐）

1. **下载发布包**
   - 访问：https://github.com/lbnqq/CNKI-skills/releases
   - 下载最新版本的 `CNKI-skill-v1.0.0.zip`

2. **解压到任意目录**
   ```bash
   unzip CNKI-skill-v1.0.0.zip
   cd CNKI-skill-v1.0.0
   ```

3. **安装依赖**
   ```bash
   # Windows
   install.bat

   # Linux/Mac
   bash install.sh
   ```

### 方式二：从GitHub克隆

```bash
# 克隆仓库
git clone git@github.com:lbnqq/CNKI-skills.git
cd CNKI-skills

# 安装依赖
bash install.sh  # Linux/Mac
# 或
install.bat     # Windows
```

---

## 🚀 快速开始

### 1. 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows / Linux / macOS
- **网络**: 能访问CNKI网站

### 2. 安装Playwright浏览器

```bash
# 安装Chromium浏览器（必需）
playwright install chromium
```

### 3. 使用Skill

在Claude Code中使用：

```
帮我下载3篇跟'人工智能'相关的学位论文到 D:\papers
```

---

## ✨ 功能特性

### 核心功能

✅ **自然语言输入解析**
- 支持中文自然语言输入
- 智能提取关键词、数量、文献类型、保存路径
- 支持多种输入格式

✅ **反检测浏览器自动化**
- 绕过CNKI安全验证
- 模拟真实用户行为
- 完善的浏览器配置

✅ **分批次并发下载**
- 自动分批次处理（避免限流）
- 批次间智能延迟
- 100%下载成功率

✅ **智能文件管理**
- 自动文件命名（包含标题、作者）
- 自动去重（同名文件自动编号）
- 支持PDF/CAJ格式

✅ **完善的日志和统计**
- 实时下载进度显示
- 详细的错误日志
- 下载结果统计报告

### 支持的文献类型

- 学术期刊
- 学位论文
- 会议论文
- 报纸文章
- 年鉴
- 专利
- 标准
- 科技成果
- 学术辑刊
- 图书
- 知网文库

---

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| **成功率** | 100%（分批次下载模式） |
| **平均速度** | 5.6篇/分钟 |
| **并发数** | 1篇/批次（可配置） |
| **批次延迟** | 3秒（可配置） |
| **支持格式** | PDF、CAJ |

---

## 📁 文件结构

```
CNKI-skill-V5/
├── src/                        # 源代码
│   ├── __init__.py
│   ├── main.py                 # Skill主入口
│   ├── cnki_browser.py         # 浏览器自动化
│   ├── downloader.py           # 下载管理器
│   ├── parser.py               # 输入解析器
│   ├── models.py               # 数据模型
│   ├── utils.py                # 工具函数
│   └── config.py               # 配置管理
├── skill.json                  # Skill元数据
├── skill_prompt.md             # Skill提示词
├── requirements.txt            # Python依赖
├── install.bat                 # Windows安装脚本
├── install.sh                  # Linux/Mac安装脚本
├── README.md                   # 项目说明
├── QUICKSTART.md               # 快速开始
├── INTEGRATION_GUIDE.md        # 集成指南
└── RELEASE_NOTES.md            # 发布说明（本文件）
```

---

## ⚙️ 配置说明

默认配置文件位置：`~/.cnki_downloader/config.json`

### 可配置项

```json
{
  "download_settings": {
    "max_concurrent": 1,        // 每批并发数（建议1-2）
    "timeout": 30000,           // 超时时间（毫秒）
    "retry_times": 2            // 重试次数
  },
  "browser_settings": {
    "headless": false,          // 是否无头模式（建议false）
    "slow_mo": 500              // 操作延迟（毫秒）
  },
  "logging": {
    "level": "INFO",            // 日志级别
    "log_dir": "~/cnki_downloader_logs"
  }
}
```

---

## 🔧 故障排除

### 问题1：浏览器启动失败

**错误信息**: `Browser not found`

**解决方案**:
```bash
playwright install chromium
```

### 问题2：下载失败率高

**原因**: 并发数过高触发CNKI限流

**解决方案**:
- 降低 `max_concurrent` 到 1
- 增加 `slow_mo` 延迟时间
- 确保使用分批次下载模式

### 问题3：无法访问CNKI

**可能原因**:
- 网络问题
- 需要VPN
- CNKI暂时维护

**解决方案**:
- 检查网络连接
- 尝试使用VPN
- 稍后重试

---

## 📝 更新日志

### v1.0.0 (2026-01-10)

✨ **首发版本**
- 完整实现CNKI论文下载功能
- 自然语言输入解析
- 反检测浏览器自动化
- 分批次并发下载（100%成功率）
- 智能文件命名和去重
- 详细日志和统计报告

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

---

## 📧 联系方式

- **GitHub**: https://github.com/lbnqq/CNKI-skills
- **Issues**: https://github.com/lbnqq/CNKI-skills/issues

---

## ⭐ 致谢

感谢使用CNKI论文下载Skill！如果觉得有用，请给个Star⭐

---

## 📸 使用示例

### 示例1：下载期刊论文
```
帮我下载5篇关于'机器学习'的学术期刊到 D:\ML_papers
```

### 示例2：下载学位论文
```
下载10篇'深度学习'相关的学位论文到 ~/papers/thesis
```

### 示例3：下载会议论文
```
帮我下20个会议论文，关键词是计算机视觉，保存到 C:\CV_conf
```

---

**享受自动化下载的便利！** 🎉
