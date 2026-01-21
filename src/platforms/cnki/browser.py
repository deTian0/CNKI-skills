"""
CNKI论文下载器 - CNKI浏览器操作
封装所有与CNKI网站的交互操作
"""

import asyncio
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser, BrowserContext, Download

from src.platforms.base import PlatformBase
from src.core.models import Paper, DownloadResult, DownloadStatus, ErrorLog
from src.utils import sanitize_filename, generate_unique_filename, setup_logging


class CNKIBrowser(PlatformBase):
    """CNKI浏览器操作封装"""

    # CNKI URL
    CNKI_HOME = "https://kc.cnki.net/"

    # 文献类型选择器（基于页面视图分析）
    # 使用text-is进行精确文本匹配，避免匹配到包含相同文字的其他元素
    DOC_TYPE_SELECTORS = {
        "学术期刊": "a:text-is('学术期刊')",
        "学位论文": "a:text-is('学位论文')",
        "会议": "a:text-is('会议')",
        "报纸": "a:text-is('报纸')",
        "年鉴": "a:text-is('年鉴')",
        "专利": "a:text-is('专利')",
        "标准": "a:text-is('标准')",
        "成果": "a:text-is('成果')",
        "学术辑刊": "a:text-is('学术辑刊')",
        "图书": "a:text-is('图书')",
        "文库": "a:text-is('文库')",
    }

    # 检索框选择器（多种策略）
    SEARCH_INPUT_SELECTORS = [
        "input[class*='n-input__input']",  # 优先使用，选择第一个匹配的元素
        "input[placeholder*='文献']",
        "input[type='text'].search-input",
        "input[class*='search']",
        "/html/body/div[1]/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/input",
        '//*[@id="layoutContainer"]/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/input'
    ]

    # 检索按钮选择器
    SEARCH_BUTTON_SELECTORS = [
        "button:has-text('检索')",
        "input[type='submit'][value*='检索']",
        ".search-btn",
    ]

    # 论文列表项选择器
    # PAPER_ITEM_SELECTOR = ".result-table-list tr"
    PAPER_ITEM_SELECTOR = ".n-data-table-tbody tr"
    # 备用选择器
    PAPER_ITEM_SELECTOR_ALT = ("#layoutContainer > div.main-view > div > div.main-content-wrap >"
                               " div.main-content > div > div.main > div > div.result-main-list.box-shadow > "
                               "div.main-list__content > div.n-data-table.n-data-table--bottom-bordered.n-data-table--single-line.result-list.has-selection > div > div > div > div.n-scrollbar-container > div > table > tbody > tr")

    # 下载按钮选择器（支持button和a标签）
    PDF_DOWNLOAD_SELECTOR = "button:has-text('PDF下载'), button .n-button__content:text-is('PDF下载'), a:has-text('PDF下载')"
    CAJ_DOWNLOAD_SELECTOR = "button:has-text('CAJ下载'), button .n-button__content:text-is('CAJ下载'), a:has-text('CAJ下载')"
    
    # 标题选择器列表
    TITLE_SELECTORS = ["a.title", ".name a", "a[href*='detail']", "td a", "a"]

    def __init__(
            self,
            download_dir: Path,
            config=None,
            headless: bool = False,
            slow_mo: int = 500,
            timeout: int = 30000,
            viewport_width: int = 1366,
            viewport_height: int = 768,
            locale: str = "zh-CN",
            timezone: str = "Asia/Shanghai",
            browser_args: list = None,
            user_agent: str = None,
            logger=None
    ):
        """
        初始化浏览器

        Args:
            download_dir: 下载保存目录
            config: 配置对象（优先使用，如果提供则覆盖其他参数）
            headless: 是否无头模式
            slow_mo: 操作延迟（毫秒）
            timeout: 超时时间（毫秒）
            viewport_width: 视口宽度
            viewport_height: 视口高度
            locale: 语言设置
            timezone: 时区
            browser_args: 浏览器启动参数
            user_agent: 用户代理字符串
            logger: 日志对象
        """
        self.config = config
        self.download_dir = download_dir
        
        # 优先使用 config，否则使用传入的参数
        if config and hasattr(config, 'browser'):
            browser_settings = config.browser
            self.headless = browser_settings.headless
            self.slow_mo = browser_settings.slow_mo
            self.timeout = config.download.timeout if hasattr(config, 'download') else timeout
            self.viewport_width = browser_settings.viewport_width
            self.viewport_height = browser_settings.viewport_height
            self.locale = browser_settings.locale
            self.timezone = browser_settings.timezone
            self.browser_args = browser_settings.args if browser_settings.args else browser_args
            self.user_agent = browser_settings.user_agent or user_agent
        else:
            self.headless = headless
            self.slow_mo = slow_mo
            self.timeout = timeout
            self.viewport_width = viewport_width
            self.viewport_height = viewport_height
            self.locale = locale
            self.timezone = timezone
            self.browser_args = browser_args or []
            self.user_agent = user_agent or (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        self.logger = logger or setup_logging(download_dir / "logs")

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def start(self) -> None:
        """启动浏览器"""
        try:
            self.logger.info("正在启动浏览器（使用反检测配置）...")
            self.playwright = await async_playwright().start()

            # 使用反检测参数启动浏览器
            launch_options = {
                "headless": self.headless,
                "slow_mo": self.slow_mo,
            }

            # 添加浏览器启动参数
            if self.browser_args:
                launch_options["args"] = self.browser_args

            self.logger.debug(f"浏览器启动参数: {launch_options}")
            self.browser = await self.playwright.chromium.launch(**launch_options)

            # 创建浏览器上下文，使用更真实的配置
            self.context = await self.browser.new_context(
                accept_downloads=True,
                viewport={'width': self.viewport_width, 'height': self.viewport_height},
                locale=self.locale,
                timezone_id=self.timezone,
                user_agent=self.user_agent,
                # 添加额外的权限和特性
                permissions=["geolocation", "notifications"],
                color_scheme="light",  # 使用浅色模式
                # 添加更多真实用户的HTTP头
                extra_http_headers={
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }
            )

            # 创建新页面
            self.page = await self.context.new_page()

            # 在页面中添加一些初始化脚本，进一步隐藏自动化特征
            await self.page.add_init_script("""
                // 覆盖navigator.webdriver属性
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });

                // 覆盖chrome对象
                window.chrome = {
                    runtime: {},
                };

                // 覆盖permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );

                // 覆盖plugins长度
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });

                // 覆盖languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en'],
                });
            """)

            self.logger.info("✓ 浏览器启动成功（已应用反检测配置）")

        except Exception as e:
            self.logger.error(f"❌ 启动浏览器失败: {e}")
            raise

    async def close(self) -> None:
        """关闭浏览器"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

            self.logger.info("✓ 浏览器已关闭")
        except Exception as e:
            self.logger.error(f"❌ 关闭浏览器时出错: {e}")

    async def _wait_for_page_load(self, timeout: int = None):
        """等待页面加载完成（公共方法）"""
        if timeout is None:
            timeout = self.config.browser.page_load_timeout if self.config and hasattr(self.config, 'browser') else 15000
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
        except:
            await self.page.wait_for_load_state("load", timeout=timeout)

    async def _check_and_switch_to_new_page(
            self,
            old_url: str,
            initial_pages: dict,
            initial_page_count: int,
            url_keywords: List[str] = None,
            wait_time: int = None,
            action_description: str = "操作"
    ) -> Optional[Page]:
        """
        检查并切换到新打开的页面（公共方法）

        Args:
            old_url: 操作前的页面URL
            initial_pages: 操作前所有页面的URL字典 {url: page}
            initial_page_count: 操作前的页面数量
            url_keywords: 用于查找目标页面的URL关键词列表（如["search", "result"]）
            wait_time: 等待新页面打开的时间（秒），如果为None则使用配置
            action_description: 操作描述（用于日志）

        Returns:
            找到的目标页面，如果没有找到则返回None
        """
        # 等待页面响应（可能是跳转或打开新标签页）
        if wait_time is None:
            wait_time = self.config.browser.page_switch_wait_time if self.config and hasattr(self.config, 'browser') else 2
        await asyncio.sleep(wait_time)

        # 检查所有页面，找到新打开的页面或URL改变的页面
        target_page = None
        current_pages = list(self.context.pages)
        current_page_count = len(current_pages)

        # 策略1: 检查是否有新页面打开
        if current_page_count > initial_page_count:
            # 有新页面打开，检查所有新页面
            for page in current_pages:
                if page.url not in initial_pages:
                    # 这是一个新页面
                    target_page = page
                    self.logger.info(f"✓ 检测到新标签页: {page.url}")
                    break

            # 如果没有找到新页面，使用最后一个页面
            if not target_page and current_pages:
                last_page = current_pages[-1]
                if last_page.url != old_url:
                    target_page = last_page
                    self.logger.info(f"✓ 使用最后一个页面: {last_page.url}")

        # 策略2: 检查当前页面URL是否改变
        if not target_page:
            new_url = self.page.url
            if new_url != old_url:
                target_page = self.page
                self.logger.info(f"✓ 当前页面已跳转: {old_url} -> {new_url}")

        # 策略3: 如果提供了URL关键词，检查所有页面找到包含关键词的页面
        if not target_page and url_keywords:
            for page in current_pages:
                page_url = page.url.lower()
                for keyword in url_keywords:
                    if keyword in page_url and page.url != old_url:
                        target_page = page
                        self.logger.info(f"✓ 找到包含'{keyword}'的页面: {page.url}")
                        break
                if target_page:
                    break

        # 策略4: 检查所有页面，找到URL不同的页面
        if not target_page:
            for page in current_pages:
                if page.url != old_url and page.url != self.page.url:
                    target_page = page
                    self.logger.info(f"✓ 找到URL不同的页面: {page.url}")
                    break

        # 切换到目标页面并等待加载
        if target_page and target_page != self.page:
            self.page = target_page
            self.logger.info(f"✓ 已切换到目标页面: {self.page.url}")
        elif not target_page:
            self.logger.warning(f"未找到目标页面，使用当前页面")
        
        # 统一等待页面加载
        await self._wait_for_page_load()

        # 延迟检测：再次检查所有页面
        if not target_page:
            await asyncio.sleep(1)
            for page in self.context.pages:
                page_url = page.url.lower()
                if url_keywords and any(k in page_url for k in url_keywords) or not url_keywords:
                    if page.url != self.page.url:
                        self.page = page
                        self.logger.info(f"✓ 延迟检测到目标页面: {self.page.url}")
                        await self._wait_for_page_load()
                        return self.page

        return target_page

    async def goto_homepage(self) -> Page:
        """
        导航到CNKI首页

        Returns:
            Page对象
        """
        try:
            self.logger.info(f"正在访问CNKI首页: {self.CNKI_HOME}")

            await self.page.goto(
                self.CNKI_HOME,
                timeout=self.timeout,
                wait_until="networkidle"
            )

            # 等待页面加载完成
            await self.page.wait_for_load_state("networkidle")

            self.logger.info("✓ 已访问CNKI首页")

            return self.page

        except Exception as e:
            self.logger.error(f"❌ 访问CNKI首页失败: {e}")
            raise

    async def select_document_type(self, doc_type: str) -> Page:
        """
        选择文献类型

        Args:
            doc_type: 文献类型（中文）

        Returns:
            Page对象
        """
        try:
            self.logger.info(f"正在选择文献类型 self.page: {self.page}")
            self.logger.info(f"正在选择文献类型: {doc_type}")

            # 获取选择器
            selector = self.DOC_TYPE_SELECTORS.get(doc_type)
            if not selector:
                raise ValueError(f"未知的文献类型: {doc_type}")

            # 等待页面完全加载
            await self.page.wait_for_load_state("domcontentloaded")
            content_load_wait = self.config.browser.content_load_wait_time if self.config and hasattr(self.config, 'browser') else 2
            await asyncio.sleep(content_load_wait)  # 额外等待，确保动态内容加载

            # 等待页面稳定
            network_idle_timeout = self.config.browser.network_idle_timeout if self.config and hasattr(self.config, 'browser') else 10000
            try:
                await self.page.wait_for_load_state("networkidle", timeout=network_idle_timeout)
            except:
                pass  # 忽略超时，继续执行

            # 尝试多种选择器策略
            element = None
            selectors_to_try = [
                selector,  # 原始选择器 a:text-is('学术期刊')
                f"a:has-text('{doc_type}')",  # 使用has-text
                f"text='{doc_type}'",  # 直接文本匹配
                f"//a[contains(text(), '{doc_type}')]",  # XPath包含文本
                f"//a[text()='{doc_type}']",  # XPath精确匹配
                f"a >> text='{doc_type}'",  # Playwright文本选择器
            ]

            selector_timeout = self.config.browser.selector_timeout if self.config and hasattr(self.config, 'browser') else 8000
            for sel in selectors_to_try:
                try:
                    self.logger.debug(f"尝试选择器: {sel}")
                    element = await self.page.wait_for_selector(
                        sel,
                        timeout=selector_timeout,  # 每个选择器尝试时间
                        state="visible"  # 确保元素可见
                    )
                    if element:
                        # 验证元素是否真的包含目标文本
                        element_text = await element.inner_text()
                        if doc_type in element_text or element_text.strip() == doc_type:
                            self.logger.info(f"✓ 找到元素，使用选择器: {sel}, 文本: '{element_text}'")
                            break
                        else:
                            element = None  # 文本不匹配，继续尝试
                except Exception as e:
                    self.logger.debug(f"选择器 {sel} 失败: {e}")
                    continue

            if not element:
                # 如果所有选择器都失败，尝试滚动页面并再次查找
                self.logger.info("尝试滚动页面查找元素...")
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                scroll_wait = self.config.browser.scroll_wait_time if self.config and hasattr(self.config, 'browser') else 1
                await asyncio.sleep(scroll_wait)

                # 再次尝试原始选择器
                selector_retry_timeout = self.config.browser.selector_retry_timeout if self.config and hasattr(self.config, 'browser') else 10000
                try:
                    element = await self.page.wait_for_selector(
                        selector,
                        timeout=selector_retry_timeout,
                        state="visible"
                    )
                except:
                    pass

            if not element:
                # 尝试使用JavaScript直接查找元素
                self.logger.info("尝试使用JavaScript查找元素...")
                try:
                    js_result = await self.page.evaluate(f"""
                        (function() {{
                            const targetText = '{doc_type}';
                            const links = document.querySelectorAll('a');
                            for (let link of links) {{
                                const text = link.innerText || link.textContent || '';
                                if (text.trim() === targetText || text.includes(targetText)) {{
                                    // 标记元素以便后续查找
                                    link.setAttribute('data-cnki-target', 'true');
                                    return {{
                                        found: true,
                                        text: text.trim(),
                                        href: link.href
                                    }};
                                }}
                            }}
                            return {{ found: false }};
                        }})();
                    """)

                    if js_result and js_result.get('found'):
                        self.logger.info(
                            f"✓ JavaScript找到元素，文本: '{js_result.get('text')}', 链接: {js_result.get('href')}")
                        # 使用标记查找元素
                        element = await self.page.query_selector('a[data-cnki-target="true"]')
                        if element:
                            # 清除标记
                            await self.page.evaluate(
                                'document.querySelector("a[data-cnki-target]").removeAttribute("data-cnki-target")')
                except Exception as e:
                    self.logger.debug(f"JavaScript查找失败: {e}")

            if not element:
                # 最后尝试：查找所有包含该文本的链接
                self.logger.info("尝试查找所有包含文本的链接...")
                all_links = await self.page.query_selector_all("a")
                self.logger.debug(f"页面中共找到 {len(all_links)} 个链接")

                # 收集所有链接文本用于调试
                link_texts = []
                for link in all_links:
                    try:
                        text = await link.inner_text()
                        text = text.strip()
                        if text:
                            link_texts.append(text)
                            # 精确匹配或包含匹配
                            if text == doc_type or doc_type in text:
                                element = link
                                self.logger.info(f"✓ 通过文本匹配找到元素: '{text}'")
                                break
                    except:
                        continue

                # 如果还没找到，输出所有链接文本用于调试
                if not element:
                    self.logger.warning(f"未找到包含'{doc_type}'的链接")
                    # 输出所有链接文本（去重）
                    unique_texts = list(set(link_texts))[:30]
                    self.logger.debug(f"页面中的链接文本（前30个，去重）: {unique_texts}")

                    # 尝试截图保存用于调试
                    try:
                        screenshot_path = self.download_dir / "debug_screenshot.png"
                        await self.page.screenshot(path=str(screenshot_path), full_page=True)
                        self.logger.info(f"已保存页面截图到: {screenshot_path}")
                    except Exception as e:
                        self.logger.debug(f"无法保存截图: {e}")

                    # 尝试查找包含部分文本的链接（更宽松的匹配）
                    for link in all_links:
                        try:
                            text = await link.inner_text()
                            text = text.strip()
                            # 尝试部分匹配（至少匹配2个字符）
                            if len(doc_type) >= 2:
                                for i in range(len(doc_type) - 1):
                                    keyword = doc_type[i:i + 2]
                                    if keyword in text:
                                        element = link
                                        self.logger.info(
                                            f"✓ 通过部分文本匹配找到元素: '{text}' (匹配关键词: '{keyword}')")
                                        break
                                if element:
                                    break
                        except:
                            continue

            if not element:
                # 输出页面URL和标题用于调试
                page_url = self.page.url
                page_title = await self.page.title()
                self.logger.error(f"当前页面URL: {page_url}")
                self.logger.error(f"当前页面标题: {page_title}")
                raise Exception(f"无法找到文献类型链接: {doc_type}。请检查页面结构是否已更改。")

            # 滚动到元素位置
            await element.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)

            # 点击链接（可能会打开新标签页，也可能在当前页面跳转）
            old_url = self.page.url
            self.logger.debug(f"点击前页面URL: {old_url}")

            # 记录当前所有页面的URL
            initial_pages = {page.url: page for page in self.context.pages}
            initial_page_count = len(self.context.pages)

            # 先点击链接
            await element.click()
            self.logger.info(f"✓ 已点击'{doc_type}'链接")

            # 使用公共方法检查并切换到新页面
            await self._check_and_switch_to_new_page(
                old_url=old_url,
                initial_pages=initial_pages,
                initial_page_count=initial_page_count,
                url_keywords=["search"],  # 查找包含"search"的页面
                wait_time=2,
                action_description=f"点击'{doc_type}'链接"
            )

            self.logger.info(f"✓ 已进入{doc_type}库页面，当前页面URL: {self.page.url}")

            return self.page

        except Exception as e:
            self.logger.error(f"❌ 选择文献类型失败: {e}")
            raise

    async def search(self, keyword: str) -> Page:
        """
        执行检索

        Args:
            keyword: 检索关键词

        Returns:
            Page对象
        """
        try:
            self.logger.info(f"正在执行检索: {keyword}")
            self.logger.debug(f"当前页面URL: {self.page.url}")

            # 查找搜索框
            search_input = await self._find_search_input()
            if not search_input:
                raise Exception("无法定位搜索框")

            # 清空并输入关键词
            # 记录搜索前的状态（在按回车之前）
            old_url = self.page.url
            self.logger.debug(f"搜索前页面URL: {old_url}")
            initial_pages = {page.url: page for page in self.context.pages}
            initial_page_count = len(self.context.pages)

            await search_input.fill("")
            await search_input.fill(keyword)
            await search_input.press("Enter")  # 按回车也可以触发检索
            self.logger.info(f"✓ 已输入关键词: {keyword}")

            # 在按回车后使用公共方法检测新页面（按回车后可能会打开新标签页）
            await self._check_and_switch_to_new_page(
                old_url=old_url,
                initial_pages=initial_pages,
                initial_page_count=initial_page_count,
                url_keywords=["search", "result"],  # 查找包含"search"或"result"的页面
                wait_time=2,
                action_description="执行搜索"
            )

            # 等待结果页加载
            self.logger.info("等待搜索结果页面加载...")
            await self._wait_for_page_load()
            await asyncio.sleep(1)  # 额外等待1秒，确保动态内容开始加载

            # 等待结果列表出现（使用多种策略）
            result_found = False
            selectors_to_try = [
                (self.PAPER_ITEM_SELECTOR, "主选择器"),
                (self.PAPER_ITEM_SELECTOR_ALT, "备用选择器"),
            ]

            # 使用轮询方式等待结果出现（最多等待30秒）
            max_wait_time = 30
            check_interval = 1
            elapsed_time = 0

            while elapsed_time < max_wait_time and not result_found:
                for selector, selector_name in selectors_to_try:
                    try:
                        # 使用 JavaScript 检查元素是否存在且可见
                        # 使用 JavaScript 检查元素是否存在且可见
                        js_check = await self.page.evaluate(f"""
                            (function() {{
                                const elements = document.querySelectorAll('{selector}');
                                if (elements.length > 0) {{
                                    // 检查至少有一个元素可见
                                    for (let elem of elements) {{
                                        const rect = elem.getBoundingClientRect();
                                        if (rect.width > 0 && rect.height > 0) {{
                                            return {{ found: true, count: elements.length }};
                                        }}
                                    }}
                                }}
                                return {{ found: false, count: 0 }};
                            }})();
                        """)

                        if js_check and js_check.get('found') and js_check.get('count', 0) > 0:
                            self.logger.info(f"✓ 使用{selector_name}找到 {js_check.get('count')} 个结果项")
                            result_found = True
                            break
                    except Exception as e:
                        self.logger.debug(f"{selector_name}检查失败: {e}")
                        continue

                if not result_found:
                    await asyncio.sleep(check_interval)
                    elapsed_time += check_interval
                    if elapsed_time % 5 == 0:  # 每5秒输出一次日志
                        self.logger.debug(f"等待搜索结果... ({elapsed_time}/{max_wait_time}秒)")

            # 如果还没找到，尝试滚动页面并再次查找
            if not result_found:
                self.logger.info("未找到结果列表，尝试滚动页面...")
                try:
                    # 滚动到页面中间
                    await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                    await asyncio.sleep(2)  # 等待内容加载

                    # 再次尝试主选择器
                    for selector, selector_name in selectors_to_try[:2]:  # 只尝试前两个
                        try:
                            items = await self.page.query_selector_all(selector)
                            if items and len(items) > 0:
                                self.logger.info(f"✓ 滚动后使用{selector_name}找到 {len(items)} 个结果项")
                                result_found = True
                                break
                        except:
                            continue
                except Exception as e:
                    self.logger.debug(f"滚动操作失败: {e}")

            # 如果仍然没找到，输出调试信息
            if not result_found:
                self.logger.warning("未找到搜索结果列表")
                # 尝试截图
                try:
                    screenshot_path = self.download_dir / "search_result_debug.png"
                    await self.page.screenshot(path=str(screenshot_path), full_page=True)
                    self.logger.info(f"已保存搜索结果页面截图到: {screenshot_path}")
                except Exception as e:
                    self.logger.debug(f"无法保存截图: {e}")

                # 输出页面信息
                page_url = self.page.url
                page_title = await self.page.title()
                self.logger.debug(f"当前页面URL: {page_url}")
                self.logger.debug(f"当前页面标题: {page_title}")

                # 检查是否有错误提示
                try:
                    error_elements = await self.page.query_selector_all(".error, .no-result, .empty")
                    if error_elements:
                        for elem in error_elements:
                            text = await elem.inner_text()
                            if text:
                                self.logger.warning(f"页面提示: {text}")
                except:
                    pass

                # 不抛出异常，继续执行（可能页面结构已变化，但可以尝试继续）
                self.logger.warning("⚠️ 未找到结果列表，但将继续执行...")

            self.logger.info("✓ 检索完成，结果页已加载")

            return self.page

        except Exception as e:
            self.logger.error(f"❌ 执行检索失败: {e}")
            raise

    async def get_paper_list(self, count: int) -> List[Paper]:
        """
        获取论文列表

        Args:
            count: 需要获取的论文数量

        Returns:
            论文列表
        """
        try:
            self.logger.info(f"正在获取前 {count} 篇论文信息...")

            papers = []
            page_num = 1

            while len(papers) < count:
                self.logger.info(f"正在获取第 {page_num} 页...")

                # 获取当前页的论文列表
                page_papers = await self.get_papers_from_current_page()

                if not page_papers:
                    self.logger.warning("当前页没有找到论文，停止获取")
                    break

                papers.extend(page_papers)
                self.logger.info(f"✓ 已获取 {len(page_papers)} 篇论文")

                # 如果已获取足够的论文，停止
                if len(papers) >= count:
                    papers = papers[:count]  # 截取需要的数量
                    break

                # 尝试翻页
                if not await self.goto_next_page():
                    break
                page_num += 1

            self.logger.info(f"✓ 共获取 {len(papers)} 篇论文信息")

            return papers

        except Exception as e:
            self.logger.error(f"❌ 获取论文列表失败: {e}")
            raise

    async def get_papers_from_current_page(self) -> List[Paper]:
        """
        从当前页提取论文信息

        Returns:
            当前页的论文列表
        """
        papers = []
        self.logger.info("=" * 60)
        self.logger.info("开始从当前页提取论文信息...")
        self.logger.debug(f"当前页面URL: {self.page.url}")

        try:
            # 尝试主选择器
            self.logger.debug(f"尝试使用主选择器: {self.PAPER_ITEM_SELECTOR}")
            items = await self.page.query_selector_all(self.PAPER_ITEM_SELECTOR)
            self.logger.info(f"主选择器找到 {len(items)} 个项目")

            # 如果主选择器失败，尝试备用选择器
            if not items:
                self.logger.debug(f"主选择器未找到项目，尝试备用选择器: {self.PAPER_ITEM_SELECTOR_ALT}")
                items = await self.page.query_selector_all(self.PAPER_ITEM_SELECTOR_ALT)
                self.logger.info(f"备用选择器找到 {len(items)} 个项目")

            if not items:
                self.logger.warning("未找到任何论文项目")
                return papers

            self.logger.info(f"共找到 {len(items)} 个论文项目，开始提取信息...")

            for index, item in enumerate(items, 1):
                try:
                    self.logger.debug(f"--- 处理第 {index}/{len(items)} 个项目 ---")

                    # 提取标题
                    title_elem = None
                    for selector in self.TITLE_SELECTORS:
                        title_elem = await item.query_selector(selector)
                        if title_elem:
                            break
                    
                    if not title_elem:
                        self.logger.warning(f"  第 {index} 个项目: 未找到标题元素，跳过")
                        continue
                    
                    title = (await title_elem.inner_text()).strip()
                    if not title:
                        self.logger.warning(f"  第 {index} 个项目: 标题为空，跳过")
                        continue
                    
                    self.logger.debug(f"  提取到标题: {title[:50]}{'...' if len(title) > 50 else ''}")
                    
                    # 创建论文对象
                    paper = Paper(title=title)

                    # 提取可选字段（作者、来源、年份）
                    paper.authors = await self._extract_field(item, "author", [".author", "td:nth-child(2)", "[class*='author']"])
                    paper.source = await self._extract_field(item, "source", [".source", "td:nth-child(3)", "[class*='source']"])
                    paper.year = await self._extract_field(item, "year", [".date", "td:nth-child(4)", "[class*='date'], [class*='year']"])

                    # 提取详情页URL
                    paper.url = await title_elem.get_attribute("href") if title_elem else None
                    if paper.url:
                        self.logger.debug(f"  提取到URL: {paper.url}")

                    papers.append(paper)
                    self.logger.info(f"  ✓ 第 {index} 篇论文提取成功: {title[:50]}...")

                except Exception as e:
                    self.logger.warning(f"  第 {index} 个项目提取论文信息时出错: {e}", exc_info=True)
                    continue

        except Exception as e:
            self.logger.error(f"解析论文列表时出错: {e}", exc_info=True)

        self.logger.info(f"提取完成，共提取到 {len(papers)} 篇论文")
        self.logger.info("=" * 60)
        return papers

    async def download_paper(self, paper: Paper) -> DownloadResult:
        """
        下载单篇论文

        Args:
            paper: 论文对象

        Returns:
            DownloadResult对象
        """
        start_time = datetime.now()

        try:
            self.logger.info(f"正在下载: {paper.title[:50]}...")

            # 如果没有详情页URL，从列表页直接下载
            if not paper.url:
                # 尝试在当前页找到对应的下载按钮
                return await self._download_from_list_page(paper)

            # 如果有详情页URL，先进入详情页
            else:
                return await self._download_from_detail_page(paper)

        except Exception as e:
            # 下载失败
            elapsed = (datetime.now() - start_time).total_seconds()

            error_log = ErrorLog(
                error_code="E005",
                error_message=str(e),
                paper_title=paper.title
            )

            return DownloadResult(
                paper=paper,
                status=DownloadStatus.FAILED,
                error_message=str(e),
                download_time=elapsed
            )

    async def _download_from_list_page(self, paper: Paper) -> DownloadResult:
        """
        从列表页直接下载（未进入详情页）

        Args:
            paper: 论文对象

        Returns:
            DownloadResult对象
        """
        start_time = datetime.now()

        try:
            # 在列表页查找该论文的行
            # 由于我们在列表页，需要找到对应论文的下载按钮

            # 这里简化处理：实际需要更复杂的逻辑来定位具体是哪一行
            # 对于MVP版本，我们假设已经点击到详情页

            self.logger.warning("从列表页下载功能需要进入详情页")
            raise Exception("需要先进入论文详情页")

        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            return DownloadResult(
                paper=paper,
                status=DownloadStatus.FAILED,
                error_message=str(e),
                download_time=elapsed
            )

    async def _find_download_button(self, button_text: str):
        """查找下载按钮（公共方法）"""
        selectors = [
            f"button:has-text('{button_text}')",
            f"button:has(.n-button__content:text-is('{button_text}'))",
            f"a:has-text('{button_text}')",
        ]
        for selector in selectors:
            try:
                download_button_timeout = self.config.browser.download_button_timeout if self.config and hasattr(self.config, 'browser') else 3000
                button = await self.page.wait_for_selector(selector, timeout=download_button_timeout, state="visible")
                if button:
                    self.logger.info(f"✓ 找到{button_text}按钮")
                    return button
            except:
                continue
        return None

    async def _find_element_by_selectors(self, selectors: List[str], timeout: int = None, description: str = "元素"):
        """通过多个选择器查找元素（公共方法）"""
        if timeout is None:
            timeout = self.config.browser.element_find_timeout if self.config and hasattr(self.config, 'browser') else 5000
        for selector in selectors:
            try:
                elem = await self.page.wait_for_selector(selector, timeout=timeout, state="visible")
                if elem and await elem.is_visible():
                    self.logger.debug(f"✓ 找到{description}，使用选择器: {selector}")
                    return elem
            except:
                continue
        return None

    async def _find_search_input(self):
        """查找搜索框（公共方法）"""
        element_find_timeout = self.config.browser.element_find_timeout if self.config and hasattr(self.config, 'browser') else 5000
        for selector in self.SEARCH_INPUT_SELECTORS:
            try:
                if selector == "input[class*='n-input__input']":
                    await self.page.wait_for_selector(selector, timeout=element_find_timeout, state="visible")
                    all_inputs = await self.page.query_selector_all(selector)
                    if all_inputs:
                        return all_inputs[0]
                else:
                    input_elem = await self.page.wait_for_selector(selector, timeout=element_find_timeout, state="visible")
                    if input_elem and await input_elem.is_visible():
                        return input_elem
            except:
                continue
        return None

    async def goto_next_page(self) -> bool:
        """
        翻到下一页

        Returns:
            是否成功翻页
        """
        try:
            # 查找"下一页"按钮
            next_button = self.page.locator("a:has-text('下一页'), a.next, button:has-text('下一页')").first
            if await next_button.is_visible():
                await next_button.click()
                await self.page.wait_for_load_state("networkidle")
                self.logger.info("✓ 已翻到下一页")
                return True
            else:
                self.logger.info("没有更多页面了")
                return False
        except Exception as e:
            self.logger.info(f"无法找到下一页按钮: {e}")
            return False

    def _normalize_url(self, url: str) -> str:
        """规范化URL（公共方法）"""
        if not url:
            raise Exception("URL为空")
        
        url = url.strip()
        if url.startswith(('http://', 'https://')):
            return url
        
        base_url = "https://kc.cnki.net" if 'kc.cnki.net' in self.page.url else "https://kns.cnki.net"
        return base_url + (url if url.startswith('/') else '/' + url.lstrip('/'))

    async def _extract_field(self, item, field_name: str, selectors: List[str]) -> Optional[str]:
        """提取字段的公共方法"""
        for selector in selectors:
            elem = await item.query_selector(selector)
            if elem:
                text = (await elem.inner_text()).strip()
                if text:
                    self.logger.debug(f"  提取到{field_name}: {text}")
                    return text
        return None

    async def _download_from_detail_page(self, paper: Paper) -> DownloadResult:
        """
        从详情页下载论文

        Args:
            paper: 论文对象（包含URL）

        Returns:
            DownloadResult对象
        """
        start_time = datetime.now()

        try:
            # 导航到详情页
            self.logger.info(f"正在进入详情页: {paper.title[:50]}...")
            self.logger.debug(f"原始URL: {paper.url}")

            # 规范化URL
            paper.url = self._normalize_url(paper.url)
            self.logger.info(f"访问URL: {paper.url}")
            await self.page.goto(paper.url, timeout=self.timeout)
            await self.page.wait_for_load_state("networkidle")

            # 查找下载按钮（PDF优先，CAJ备用）
            download_button = await self._find_download_button("PDF下载") or await self._find_download_button("CAJ下载")
            if not download_button:
                raise Exception("未找到下载按钮（PDF或CAJ）")

            # 点击下载
            self.logger.info("正在点击下载按钮...")

            async with self.page.expect_download(timeout=self.timeout) as download_info:
                await download_button.click()

            download: Download = await download_info.value

            # 确定保存文件名
            suggested_filename = download.suggested_filename
            # 转换为PDF格式（如果是CAJ）
            if suggested_filename.endswith('.caj'):
                suggested_filename = suggested_filename[:-4] + '.pdf'

            # 清理文件名
            clean_filename = sanitize_filename(
                suggested_filename.replace('.pdf', '')
            ) + '.pdf'

            # 检查文件是否已存在
            existing_files = list(self.download_dir.glob("*.pdf"))
            final_filename = generate_unique_filename(clean_filename, existing_files)

            # 保存文件
            save_path = self.download_dir / final_filename
            await download.save_as(save_path)

            elapsed = (datetime.now() - start_time).total_seconds()

            self.logger.info(f"✓ 下载成功: {final_filename}")

            return DownloadResult(
                paper=paper,
                status=DownloadStatus.SUCCESS,
                file_path=save_path,
                download_time=elapsed
            )

        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()

            # 检查是否是付费论文
            error_msg = str(e)
            if any(keyword in error_msg for keyword in ["付费", "购买", "权限", "登录"]):
                self.logger.warning(f"⚠️ 论文需要付费或权限: {paper.title[:50]}...")
                return DownloadResult(
                    paper=paper,
                    status=DownloadStatus.SKIPPED,
                    error_message="需要付费权限",
                    download_time=elapsed
                )
            else:
                raise

    def __enter__(self):
        """上下文管理器入口"""
        # 对于异步上下文管理器，需要使用 async with
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 关闭浏览器（同步版本，实际应该用async）
        pass
