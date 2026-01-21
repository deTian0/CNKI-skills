"""
系统工具函数
"""

import shutil


def disk_usage(path: str) -> object:
    """获取磁盘使用情况（跨平台）"""
    return shutil.disk_usage(path)
