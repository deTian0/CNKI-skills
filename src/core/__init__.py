"""
核心模块
包含数据模型、配置管理和输入解析
"""

from src.core.models import (
    DocumentType,
    DownloadStatus,
    DownloadRequest,
    Paper,
    DownloadResult,
    DownloadSummary,
    ErrorLog
)
from src.core.config import ConfigManager, ConfigWrapper
from src.core.parser import InputParser

__all__ = [
    "DocumentType",
    "DownloadStatus",
    "DownloadRequest",
    "Paper",
    "DownloadResult",
    "DownloadSummary",
    "ErrorLog",
    "ConfigManager",
    "ConfigWrapper",
    "InputParser",
]
