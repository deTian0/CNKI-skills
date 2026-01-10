#!/bin/bash
# CNKI论文下载器Skill - 安装脚本

echo "========================================"
echo "  CNKI论文下载器Skill - 安装向导"
echo "========================================"
echo ""

# 检查Python版本
echo "📋 步骤 1/5: 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python版本: $python_version"

# 检查pip
echo ""
echo "📋 步骤 2/5: 检查pip..."
pip3 --version >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ pip已安装"
else
    echo "❌ pip未安装，请先安装pip"
    exit 1
fi

# 安装依赖
echo ""
echo "📋 步骤 3/5: 安装Python依赖..."
echo "正在安装 playwright..."
pip3 install playwright --quiet

echo "正在安装Chromium浏览器..."
playwright install chromium --quiet

echo "✓ 依赖安装完成"

# 确定Claude Skills目录
echo ""
echo "📋 步骤 4/5: 确定安装目录..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    SKILL_DIR="$HOME/.claude/skills"
    echo "检测到系统: macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    SKILL_DIR="$HOME/.claude/skills"
    echo "检测到系统: Linux"
else
    # Windows (Git Bash)
    SKILL_DIR="$USERPROFILE/.claude/skills"
    echo "检测到系统: Windows"
fi

echo "Claude Skills目录: $SKILL_DIR"

# 复制Skill文件
echo ""
echo "📋 步骤 5/5: 安装Skill..."

# 获取当前脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "项目目录: $SCRIPT_DIR"

# 创建目标目录
TARGET_DIR="$SKILL_DIR/cnki-downloader"
mkdir -p "$TARGET_DIR"

# 复制文件
echo "正在复制文件..."
cp -r "$SCRIPT_DIR/src" "$TARGET_DIR/"
cp "$SCRIPT_DIR/skill.json" "$TARGET_DIR/"
cp "$SCRIPT_DIR/skill_prompt.md" "$TARGET_DIR/"
cp "$SCRIPT_DIR/README.md" "$TARGET_DIR/"
cp "$SCRIPT_DIR/CNKI论文下载Skill需求文档.md" "$TARGET_DIR/"

echo "✓ 文件复制完成"

# 创建配置目录
echo ""
echo "创建配置目录..."
CONFIG_DIR="$HOME/.cnki_downloader"
mkdir -p "$CONFIG_DIR"
echo "✓ 配置目录: $CONFIG_DIR"

# 创建默认配置文件
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    echo "创建默认配置..."
    cat > "$CONFIG_DIR/config.json" << EOF
{
  "download_settings": {
    "default_dir": "$HOME/Downloads/CNKI",
    "max_concurrent": 3,
    "timeout": 30000,
    "retry_times": 2
  },
  "browser_settings": {
    "headless": false,
    "slow_mo": 100
  },
  "file_settings": {
    "sanitize_filename": true,
    "max_filename_length": 200,
    "conflict_strategy": "append_number"
  },
  "default_values": {
    "doc_type": "学术期刊",
    "count": 10,
    "language": "CHS"
  },
  "logging": {
    "enabled": true,
    "level": "INFO",
    "log_dir": "$HOME/cnki_downloader_logs",
    "max_log_size": 10485760
  }
}
EOF
    echo "✓ 配置文件已创建"
fi

# 完成
echo ""
echo "========================================"
echo "  ✅ 安装完成！"
echo "========================================"
echo ""
echo "📁 安装位置: $TARGET_DIR"
echo "⚙️  配置文件: $CONFIG_DIR/config.json"
echo ""
echo "📖 使用方法："
echo "   1. 重启Claude Code"
echo "   2. 直接对话：'帮我下载5篇跟人工智能相关的学位论文到 D:\\papers\\'"
echo ""
echo "📘 查看文档: $TARGET_DIR/README.md"
echo ""
echo "🎉 开始使用吧！"
