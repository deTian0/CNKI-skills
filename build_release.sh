#!/bin/bash
# CNKI Skill 打包脚本
# 用于创建发布包

set -e

# 配置
VERSION="v1.0.0"
PACKAGE_NAME="CNKI-skill-${VERSION}"
OUTPUT_DIR="release"

echo "========================================="
echo "CNKI Skill 打包工具"
echo "========================================="
echo ""

# 创建输出目录
echo "1️⃣  创建输出目录..."
mkdir -p "${OUTPUT_DIR}"

# 删除旧的打包文件
echo "2️⃣  清理旧文件..."
rm -f "${OUTPUT_DIR}/${PACKAGE_NAME}.zip"
rm -f "${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz"

# 创建临时目录
echo "3️⃣  创建临时目录..."
TMP_DIR=$(mktemp -d)
mkdir -p "${TMP_DIR}/${PACKAGE_NAME}"

# 复制文件到临时目录（排除不需要的文件）
echo "4️⃣  复制项目文件..."
rsync -av \
    --exclude='.git/' \
    --exclude='.gitignore' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='*.log' \
    --exclude='logs/' \
    --exclude='*.pdf' \
    --exclude='*.caj' \
    --exclude='papers/' \
    --exclude='cnki_downloader_logs/' \
    --exclude='.spec-workflow/' \
    --exclude='.playwright-mcp/' \
    --exclude='.claude/' \
    --exclude='release/' \
    --exclude='test_output/' \
    --exclude='temp/' \
    --exclude='*.session' \
    --exclude='.DS_Store' \
    --exclude='Thumbs.db' \
    ./ "${TMP_DIR}/${PACKAGE_NAME}/"

# 创建版本信息文件
echo "5️⃣  创建版本信息..."
cat > "${TMP_DIR}/${PACKAGE_NAME}/VERSION" << EOF
Package: CNKI论文下载Skill
Version: ${VERSION}
Build Date: $(date +%Y-%m-%d)
Repository: https://github.com/lbnqq/CNKI-skills
EOF

# 创建ZIP包
echo "6️⃣  创建ZIP包..."
cd "${TMP_DIR}"
zip -r "${OUTPUT_DIR}/${PACKAGE_NAME}.zip" "${PACKAGE_NAME}/" > /dev/null

# 创建TAR.GZ包
echo "7️⃣  创建TAR.GZ包..."
tar -czf "${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}/"

# 清理临时目录
echo "8️⃣  清理临时文件..."
cd -
rm -rf "${TMP_DIR}"

# 计算文件哈希（用于验证）
echo "9️⃣  计算文件哈希..."
cd "${OUTPUT_DIR}"
if command -v md5 &> /dev/null; then
    md5 "${PACKAGE_NAME}.zip" > "${PACKAGE_NAME}.zip.md5"
    md5 "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.md5"
elif command -v md5sum &> /dev/null; then
    md5sum "${PACKAGE_NAME}.zip" > "${PACKAGE_NAME}.zip.md5"
    md5sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.md5"
fi

cd ..

# 显示文件大小
echo ""
echo "✅ 打包完成！"
echo "========================================="
echo "📦 发布包信息:"
echo ""
ls -lh "${OUTPUT_DIR}/"
echo ""
echo "📍 输出目录: $(pwd)/${OUTPUT_DIR}"
echo ""
echo "📋 下一步:"
echo "1. 测试发布包: unzip -l ${OUTPUT_DIR}/${PACKAGE_NAME}.zip"
echo "2. 上传到GitHub Releases"
echo "3. 更新RELEASE_NOTES.md"
echo ""
echo "========================================="
