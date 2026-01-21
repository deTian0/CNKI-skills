"""
文本处理工具函数
"""

import re


def extract_paper_info_from_text(text: str) -> dict:
    """从文本中提取论文信息（备用方案）"""
    info = {
        "title": "",
        "authors": "",
        "source": "",
        "year": ""
    }

    lines = text.strip().split('\n')
    if lines:
        title_line = max((line for line in lines if line.strip()), key=len, default="")
        info["title"] = title_line.strip()

    year_match = re.search(r'\b(19|20)\d{2}\b', text)
    if year_match:
        info["year"] = year_match.group(0)

    return info
