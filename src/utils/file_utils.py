"""
文件操作工具函数
"""

import re
from pathlib import Path
from typing import List
from datetime import datetime


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """清理文件名中的非法字符"""
    name = Path(filename).stem

    illegal_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for char in illegal_chars:
        name = name.replace(char, '_')

    name = name.replace('：', '_')
    name = name.replace('、', '_')
    name = name.replace('，', '_')
    name = name.replace('。', '_')
    name = name.replace('（', '_')
    name = name.replace('）', '_')
    name = name.replace('《', '_')
    name = name.replace('》', '_')

    name = re.sub(r'[_\-\.]{2,}', '_', name)
    name = '_'.join(name.split())
    name = name.strip('_.- ')

    if len(name) > max_length:
        name = name[:max_length - 3] + '...'

    if not name:
        name = "unnamed"

    return name


def generate_unique_filename(filename: str, existing_files: List[Path]) -> str:
    """生成唯一文件名（处理重名）"""
    name = Path(filename).stem
    ext = Path(filename).suffix
    existing_names = [f.stem for f in existing_files]

    if name not in existing_names:
        return filename

    counter = 1
    while True:
        new_name = f"{name}_{counter}"
        if new_name not in existing_names:
            return f"{new_name}{ext}"
        counter += 1

        if counter > 10000:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{name}_{timestamp}{ext}"


def ensure_directory(directory: Path) -> bool:
    """确保目录存在，如果不存在则创建"""
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ 无法创建目录 {directory}: {e}")
        return False


def is_valid_download_directory(directory: Path) -> tuple[bool, str | None]:
    """检查目录是否可用于下载"""
    if not directory.exists():
        try:
            directory.mkdir(parents=True)
        except Exception as e:
            return False, f"无法创建目录: {e}"

    if not directory.is_dir():
        return False, "路径不是一个目录"

    test_file = directory / f".write_test_{datetime.now().timestamp()}"
    try:
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        return False, f"没有写入权限: {e}"

    try:
        from src.utils.system_utils import disk_usage
        stat = disk_usage(str(directory))
        if stat.free < 100 * 1024 * 1024:
            return False, "磁盘空间不足（至少需要100MB）"
    except:
        pass

    return True, None
