"""
日志工具函数
"""

import logging
from pathlib import Path
from datetime import datetime
from src.core.models import ErrorLog


def setup_logging(log_dir: Path, level: str = "DEBUGER") -> logging.Logger:
    """设置日志"""
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("cnki_downloader")
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers.clear()

    log_file = log_dir / f"cnki_downloader_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def save_error_log(error_log: ErrorLog, log_dir: Path) -> None:
    """保存错误日志"""
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        error_file = log_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        error_dict = error_log.to_dict()

        def convert_paths(obj):
            """递归转换Path对象为字符串"""
            if isinstance(obj, Path):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths(item) for item in obj]
            elif isinstance(obj, tuple):
                return tuple(convert_paths(item) for item in obj)
            else:
                return obj

        error_dict = convert_paths(error_dict)

        import json
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_dict, f, indent=2, ensure_ascii=False)

        print(f"📍 错误日志已保存: {error_file}")
    except Exception as e:
        print(f"⚠️ 无法保存错误日志: {e}")
