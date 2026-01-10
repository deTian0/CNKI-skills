# -*- coding: utf-8 -*-
"""
测试下载任务
"""
import asyncio
import sys
from pathlib import Path

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.main import get_skill

async def main():
    """主函数"""
    skill = get_skill()

    # 执行下载
    user_input = r"帮我下载3篇跟'医学'相关的学位论文到 D:\papers"
    result = await skill.download_papers(user_input)

    print("\n" + result)

if __name__ == "__main__":
    asyncio.run(main())
