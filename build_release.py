#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNKI Skill 打包脚本 (跨平台版本)
"""

import os
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime

# 配置
VERSION = "v1.0.0"
PACKAGE_NAME = f"CNKI-skill-{VERSION}"
OUTPUT_DIR = Path("release")

# 需要排除的文件和目录
EXCLUDE_PATTERNS = [
    '.git/',
    '.gitignore',
    '__pycache__/',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '*.log',
    'logs/',
    '*.pdf',
    '*.caj',
    'papers/',
    'cnki_downloader_logs/',
    '.spec-workflow/',
    '.playwright-mcp/',
    '.claude/',
    'release/',
    'test_output/',
    'temp/',
    '*.session',
    '.DS_Store',
    'Thumbs.db',
    'build_release.py',
    'build_release.sh',
    'build_release.bat',
]


def should_exclude(file_path):
    """检查文件是否应该被排除"""
    file_str = str(file_path).replace('\\', '/')

    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            # 文件扩展名匹配
            if file_str.endswith(pattern[1:]):
                return True
        elif pattern.endswith('/'):
            # 目录匹配
            if pattern.replace('\\', '/') in file_str.split('/'):
                return True
        else:
            # 精确匹配或包含匹配
            if pattern in file_str:
                return True

    return False


def create_package():
    """创建发布包"""
    print("=" * 50)
    print("CNKI Skill Build Tool")
    print("=" * 50)
    print()

    # 创建输出目录
    print("[1/6] Creating output directory...")
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 清理旧文件
    print("[2/6] Cleaning old files...")
    for ext in ['.zip', '.tar.gz', '.md5']:
        old_file = OUTPUT_DIR / f"{PACKAGE_NAME}{ext}"
        if old_file.exists():
            old_file.unlink()
            print(f"   Removed: {old_file}")

    # 收集文件
    print("[3/6] Collecting project files...")
    files_to_package = []
    root_dir = Path.cwd()

    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and not should_exclude(file_path):
            # 计算相对路径
            rel_path = file_path.relative_to(root_dir)
            files_to_package.append((file_path, rel_path))

    print(f"   Found {len(files_to_package)} files")

    # 创建ZIP包
    print("[4/6] Creating ZIP package...")
    zip_path = OUTPUT_DIR / f"{PACKAGE_NAME}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path, rel_path in files_to_package:
            # 在ZIP中创建包目录
            arcname = Path(PACKAGE_NAME) / rel_path
            zipf.write(file_path, arcname)

    # 创建TAR.GZ包
    print("[5/6] Creating TAR.GZ package...")
    tar_path = OUTPUT_DIR / f"{PACKAGE_NAME}.tar.gz"
    with tarfile.open(tar_path, 'w:gz') as tarf:
        for file_path, rel_path in files_to_package:
            arcname = Path(PACKAGE_NAME) / rel_path
            tarf.add(file_path, arcname=arcname)

    # 创建版本信息文件
    print("[6/6] Creating version info...")
    version_info = OUTPUT_DIR / "VERSION.txt"
    with open(version_info, 'w', encoding='utf-8') as f:
        f.write(f"Package: CNKI论文下载Skill\n")
        f.write(f"Version: {VERSION}\n")
        f.write(f"Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Repository: https://github.com/lbnqq/CNKI-skills\n")
        f.write(f"Files: {len(files_to_package)}\n")

    # 显示结果
    print()
    print("SUCCESS! Build completed.")
    print("=" * 50)
    print("Release packages:")
    print()

    # 列出所有生成的文件
    for file in sorted(OUTPUT_DIR.iterdir()):
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"   {file.name:40} {size_mb:8.2f} MB")

    print()
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print()
    print("Next steps:")
    print("1. Test package: python -m zipfile -l release/{PACKAGE_NAME}.zip")
    print("2. Upload to GitHub Releases")
    print("3. Update RELEASE_NOTES.md")
    print()
    print("=" * 50)


if __name__ == "__main__":
    try:
        create_package()
    except Exception as e:
        print(f"\nERROR: Build failed - {e}")
        import traceback

        traceback.print_exc()
