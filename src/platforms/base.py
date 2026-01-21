"""
平台基类
定义所有学术平台需要实现的接口
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from src.core.models import Paper, DownloadResult


class PlatformBase(ABC):
    """平台基类，所有学术平台都需要继承此类"""

    @abstractmethod
    async def start(self) -> None:
        """启动浏览器"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭浏览器"""
        pass

    @abstractmethod
    async def goto_homepage(self) -> None:
        """导航到平台首页"""
        pass

    @abstractmethod
    async def select_document_type(self, doc_type: str) -> None:
        """
        选择文献类型

        Args:
            doc_type: 文献类型
        """
        pass

    @abstractmethod
    async def search(self, keyword: str) -> None:
        """
        执行检索

        Args:
            keyword: 检索关键词
        """
        pass

    @abstractmethod
    async def get_papers_from_current_page(self) -> List[Paper]:
        """
        从当前页面获取论文列表

        Returns:
            论文列表
        """
        pass

    @abstractmethod
    async def download_paper(self, paper: Paper) -> DownloadResult:
        """
        下载论文

        Args:
            paper: 论文对象

        Returns:
            下载结果
        """
        pass

    @abstractmethod
    async def goto_next_page(self) -> bool:
        """
        翻到下一页

        Returns:
            是否成功翻页
        """
        pass
