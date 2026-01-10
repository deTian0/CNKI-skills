@echo off
REM CNKI Skill 打包脚本 (Windows)
REM 用于创建发布包

setlocal enabledelayedexpansion

REM 配置
set VERSION=v1.0.0
set PACKAGE_NAME=CNKI-skill-%VERSION%
set OUTPUT_DIR=release

echo =========================================
echo CNKI Skill 打包工具 (Windows)
echo =========================================
echo.

REM 创建输出目录
echo 1️⃣  创建输出目录...
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM 删除旧的打包文件
echo 2️⃣  清理旧文件...
if exist "%OUTPUT_DIR%\%PACKAGE_NAME%.zip" del "%OUTPUT_DIR%\%PACKAGE_NAME%.zip"

REM 使用PowerShell创建ZIP包
echo 3️⃣  创建ZIP包...
powershell -Command "Compress-Archive -Path '.\*' -DestinationPath '%OUTPUT_DIR%\%PACKAGE_NAME%.zip' -Force -CompressionLevel Optimal -Exclude '*.git','*.gitignore','__pycache__','*.pyc','*.pyo','*.log','logs','*.pdf','*.caj','papers','cnki_downloader_logs','.spec-workflow','.playwright-mcp','.claude','release','test_output','temp','*.session','.DS_Store','Thumbs.db','%OUTPUT_DIR%'"

REM 创建版本信息文件
echo 4️⃣  创建版本信息...
echo Package: CNKI论文下载Skill > "%OUTPUT_DIR%\VERSION.txt"
echo Version: %VERSION% >> "%OUTPUT_DIR%\VERSION.txt"
echo Build Date: %date% %time% >> "%OUTPUT_DIR%\VERSION.txt"
echo Repository: https://github.com/lbnqq/CNKI-skills >> "%OUTPUT_DIR%\VERSION.txt"

echo.
echo ✅ 打包完成！
echo =========================================
echo 📦 发布包信息:
echo.
dir "%OUTPUT_DIR%" /B
echo.
echo 📍 输出目录: %cd%\%OUTPUT_DIR%
echo.
echo 📋 下一步:
echo 1. 测试发布包: PowerShell -Command \"Expand-Archive -Path '%OUTPUT_DIR%\%PACKAGE_NAME%.zip' -DestinationPath 'test' -Force\"
echo 2. 上传到GitHub Releases
echo 3. 更新RELEASE_NOTES.md
echo.
echo ==========================================

pause
