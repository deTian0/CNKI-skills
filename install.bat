@echo off
REM CNKI论文下载器Skill - Windows安装脚本

echo ========================================
echo   CNKI论文下载器Skill - 安装向导
echo ========================================
echo.

REM 步骤 1/5: 检查Python版本
echo 📋 步骤 1/5: 检查Python版本...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8+: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python已安装
echo.

REM 步骤 2/5: 检查pip
echo 📋 步骤 2/5: 检查pip...
pip --version
if errorlevel 1 (
    echo ❌ pip未安装
    pause
    exit /b 1
)
echo ✓ pip已安装
echo.

REM 步骤 3/5: 安装依赖
echo 📋 步骤 3/5: 安装Python依赖...
echo 正在安装 playwright...
pip install playwright --quiet

echo 正在安装Chromium浏览器...
playwright install chromium --quiet

echo ✓ 依赖安装完成
echo.

REM 步骤 4/5: 确定安装目录
echo 📋 步骤 4/5: 确定安装目录...
set "SKILL_DIR=%USERPROFILE%\.claude\skills"
echo Claude Skills目录: %SKILL_DIR%
echo.

REM 步骤 5/5: 安装Skill
echo 📋 步骤 5/5: 安装Skill...

REM 获取当前脚本所在目录
set "SCRIPT_DIR=%~dp0"
echo 项目目录: %SCRIPT_DIR%

REM 创建目标目录
set "TARGET_DIR=%SKILL_DIR%\cnki-downloader"
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

REM 复制文件
echo 正在复制文件...
xcopy /E /I /Y "%SCRIPT_DIR%src" "%TARGET_DIR%\src\" >nul
copy /Y "%SCRIPT_DIR%skill.json" "%TARGET_DIR%\" >nul
copy /Y "%SCRIPT_DIR%skill_prompt.md" "%TARGET_DIR%\" >nul
copy /Y "%SCRIPT_DIR%README.md" "%TARGET_DIR%\" >nul
copy /Y "%SCRIPT_DIR%CNKI论文下载Skill需求文档.md" "%TARGET_DIR%\" >nul

echo ✓ 文件复制完成
echo.

REM 创建配置目录
echo 创建配置目录...
set "CONFIG_DIR=%USERPROFILE%\.cnki_downloader"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"
echo ✓ 配置目录: %CONFIG_DIR%
echo.

REM 创建默认配置文件
if not exist "%CONFIG_DIR%\config.json" (
    echo 创建默认配置...

    REM 注意：Windows批处理中需要转义JSON中的特殊字符
    (
        echo {
        echo   "download_settings": {
        echo     "default_dir": "%USERPROFILE%\\Downloads\\CNKI",
        echo     "max_concurrent": 3,
        echo     "timeout": 30000,
        echo     "retry_times": 2
        echo   },
        echo   "browser_settings": {
        echo     "headless": false,
        echo     "slow_mo": 100
        echo   },
        echo   "file_settings": {
        echo     "sanitize_filename": true,
        echo     "max_filename_length": 200,
        echo     "conflict_strategy": "append_number"
        echo   },
        echo   "default_values": {
        echo     "doc_type": "学术期刊",
        echo     "count": 10,
        echo     "language": "CHS"
        echo   },
        echo   "logging": {
        echo     "enabled": true,
        echo     "level": "INFO",
        echo     "log_dir": "%USERPROFILE%\\cnki_downloader_logs",
        echo     "max_log_size": 10485760
        echo   }
        echo }
    ) > "%CONFIG_DIR%\config.json"

    echo ✓ 配置文件已创建
)

REM 完成
echo.
echo ========================================
echo   ✅ 安装完成！
echo ========================================
echo.
echo 📁 安装位置: %TARGET_DIR%
echo ⚙️  配置文件: %CONFIG_DIR%\config.json
echo.
echo 📖 使用方法：
echo    1. 重启Claude Code
echo    2. 直接对话：'帮我下载5篇跟人工智能相关的学位论文到 D:\papers\'
echo.
echo 📘 查看文档: %TARGET_DIR%\README.md
echo.
echo 🎉 开始使用吧！
echo.
pause
