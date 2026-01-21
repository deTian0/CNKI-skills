"""
CNKI论文下载器 - 配置管理
使用 Pydantic v2 管理配置，支持从环境变量加载
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class DownloadSettings(BaseModel):
    """下载设置"""
    default_dir: Path = Field(default_factory=lambda: Path.home() / "Downloads" / "CNKI")
    max_concurrent: int = Field(default=1, description="最大并发数，降低并发数避免CNKI限流")
    timeout: int = Field(default=30000, description="超时时间（毫秒）")
    retry_times: int = Field(default=2, description="重试次数")
    chunk_size: int = Field(default=1024, description="分块大小")

    @field_validator('default_dir', mode='before')
    @classmethod
    def expand_path(cls, v):
        if isinstance(v, str):
            return Path(v).expanduser()
        return v


class BrowserSettings(BaseModel):
    """浏览器设置"""
    headless: bool = Field(default=False, description="是否无头模式")
    slow_mo: int = Field(default=500, description="操作延迟（毫秒）")
    user_agent: Optional[str] = Field(default=None, description="用户代理字符串")
    viewport_width: int = Field(default=1366, description="视口宽度")
    viewport_height: int = Field(default=768, description="视口高度")
    locale: str = Field(default="zh-CN", description="语言设置")
    timezone: str = Field(default="Asia/Shanghai", description="时区")
    args: List[str] = Field(
        default_factory=lambda: [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-web-security",
        ],
        description="浏览器启动参数"
    )
    # 浏览器操作超时设置（毫秒）
    page_load_timeout: int = Field(default=15000, description="页面加载超时时间（毫秒）")
    network_idle_timeout: int = Field(default=10000, description="网络空闲超时时间（毫秒）")
    selector_timeout: int = Field(default=8000, description="选择器查找超时时间（毫秒）")
    selector_retry_timeout: int = Field(default=10000, description="选择器重试超时时间（毫秒）")
    download_button_timeout: int = Field(default=3000, description="下载按钮查找超时时间（毫秒）")
    element_find_timeout: int = Field(default=5000, description="元素查找超时时间（毫秒）")
    page_switch_wait_time: int = Field(default=2, description="页面切换等待时间（秒）")
    scroll_wait_time: int = Field(default=1, description="滚动后等待时间（秒）")
    content_load_wait_time: int = Field(default=2, description="内容加载等待时间（秒）")


class FileSettings(BaseModel):
    """文件设置"""
    sanitize_filename: bool = Field(default=True, description="是否清理文件名")
    max_filename_length: int = Field(default=200, description="最大文件名长度")
    conflict_strategy: str = Field(default="append_number", description="冲突处理策略: append_number, skip, overwrite")
    encoding: str = Field(default="utf-8", description="文件编码")


class DefaultValues(BaseModel):
    """默认值"""
    doc_type: str = Field(default="学术期刊", description="默认文献类型")
    count: int = Field(default=10, description="默认下载数量")
    language: str = Field(default="CHS", description="默认语言")
    uniplatform: str = Field(default="NZKPT", description="平台标识")


class LoggingSettings(BaseModel):
    """日志设置"""
    enabled: bool = Field(default=True, description="是否启用日志")
    level: str = Field(default="INFO", description="日志级别")
    log_dir: Path = Field(default_factory=lambda: Path.home() / "cnki_downloader_logs")
    max_log_size: int = Field(default=10485760, description="最大日志文件大小（字节）")

    @field_validator('log_dir', mode='before')
    @classmethod
    def expand_path(cls, v):
        if isinstance(v, str):
            return Path(v).expanduser()
        return v


class Config(BaseSettings):
    """总配置 - 使用 Pydantic Settings 从环境变量加载"""
    
    model_config = SettingsConfigDict(
        env_prefix="",  # 不使用前缀
        env_nested_delimiter="_",  # 使用下划线分隔嵌套字段
        case_sensitive=False,  # 不区分大小写
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 忽略额外的环境变量
        env_ignore_empty=True,  # 忽略空的环境变量
    )
    
    # 下载设置
    download_default_dir: Optional[Path] = Field(default=None, alias="DOWNLOAD_DEFAULT_DIR")
    download_max_concurrent: Optional[int] = Field(default=None, alias="DOWNLOAD_MAX_CONCURRENT")
    download_timeout: Optional[int] = Field(default=None, alias="DOWNLOAD_TIMEOUT")
    download_retry_times: Optional[int] = Field(default=None, alias="DOWNLOAD_RETRY_TIMES")
    download_chunk_size: Optional[int] = Field(default=None, alias="DOWNLOAD_CHUNK_SIZE")
    
    # 浏览器设置
    browser_headless: Optional[bool] = Field(default=None, alias="BROWSER_HEADLESS")
    browser_slow_mo: Optional[int] = Field(default=None, alias="BROWSER_SLOW_MO")
    browser_user_agent: Optional[str] = Field(default=None, alias="BROWSER_USER_AGENT")
    browser_viewport_width: Optional[int] = Field(default=None, alias="BROWSER_VIEWPORT_WIDTH")
    browser_viewport_height: Optional[int] = Field(default=None, alias="BROWSER_VIEWPORT_HEIGHT")
    browser_locale: Optional[str] = Field(default=None, alias="BROWSER_LOCALE")
    browser_timezone: Optional[str] = Field(default=None, alias="BROWSER_TIMEZONE")
    
    # 文件设置
    file_sanitize_filename: Optional[bool] = Field(default=None, alias="FILE_SANITIZE_FILENAME")
    file_max_filename_length: Optional[int] = Field(default=None, alias="FILE_MAX_FILENAME_LENGTH")
    file_conflict_strategy: Optional[str] = Field(default=None, alias="FILE_CONFLICT_STRATEGY")
    file_encoding: Optional[str] = Field(default=None, alias="FILE_ENCODING")
    
    # 默认值
    default_doc_type: Optional[str] = Field(default=None, alias="DEFAULT_DOC_TYPE")
    default_count: Optional[int] = Field(default=None, alias="DEFAULT_COUNT")
    default_language: Optional[str] = Field(default=None, alias="DEFAULT_LANGUAGE")
    default_uniplatform: Optional[str] = Field(default=None, alias="DEFAULT_UNIPLATFORM")
    
    # 日志设置
    logging_enabled: Optional[bool] = Field(default=None, alias="LOGGING_ENABLED")
    logging_level: Optional[str] = Field(default=None, alias="LOGGING_LEVEL")
    logging_log_dir: Optional[Path] = Field(default=None, alias="LOGGING_LOG_DIR")
    logging_max_log_size: Optional[int] = Field(default=None, alias="LOGGING_MAX_LOG_SIZE")
    
    def get_download_settings(self) -> DownloadSettings:
        """获取下载设置"""
        defaults = DownloadSettings()
        return DownloadSettings(
            default_dir=self.download_default_dir or defaults.default_dir,
            max_concurrent=self.download_max_concurrent if self.download_max_concurrent is not None else defaults.max_concurrent,
            timeout=self.download_timeout if self.download_timeout is not None else defaults.timeout,
            retry_times=self.download_retry_times if self.download_retry_times is not None else defaults.retry_times,
            chunk_size=self.download_chunk_size if self.download_chunk_size is not None else defaults.chunk_size,
        )
    
    def get_browser_settings(self) -> BrowserSettings:
        """获取浏览器设置"""
        defaults = BrowserSettings()
        return BrowserSettings(
            headless=self.browser_headless if self.browser_headless is not None else defaults.headless,
            slow_mo=self.browser_slow_mo if self.browser_slow_mo is not None else defaults.slow_mo,
            user_agent=self.browser_user_agent or defaults.user_agent,
            viewport_width=self.browser_viewport_width if self.browser_viewport_width is not None else defaults.viewport_width,
            viewport_height=self.browser_viewport_height if self.browser_viewport_height is not None else defaults.viewport_height,
            locale=self.browser_locale or defaults.locale,
            timezone=self.browser_timezone or defaults.timezone,
            args=defaults.args,  # 浏览器参数通常不需要从环境变量配置
            page_load_timeout=self.browser_page_load_timeout if self.browser_page_load_timeout is not None else defaults.page_load_timeout,
            network_idle_timeout=self.browser_network_idle_timeout if self.browser_network_idle_timeout is not None else defaults.network_idle_timeout,
            selector_timeout=self.browser_selector_timeout if self.browser_selector_timeout is not None else defaults.selector_timeout,
            selector_retry_timeout=self.browser_selector_retry_timeout if self.browser_selector_retry_timeout is not None else defaults.selector_retry_timeout,
            download_button_timeout=self.browser_download_button_timeout if self.browser_download_button_timeout is not None else defaults.download_button_timeout,
            element_find_timeout=self.browser_element_find_timeout if self.browser_element_find_timeout is not None else defaults.element_find_timeout,
            page_switch_wait_time=self.browser_page_switch_wait_time if self.browser_page_switch_wait_time is not None else defaults.page_switch_wait_time,
            scroll_wait_time=self.browser_scroll_wait_time if self.browser_scroll_wait_time is not None else defaults.scroll_wait_time,
            content_load_wait_time=self.browser_content_load_wait_time if self.browser_content_load_wait_time is not None else defaults.content_load_wait_time,
        )
    
    def get_file_settings(self) -> FileSettings:
        """获取文件设置"""
        defaults = FileSettings()
        return FileSettings(
            sanitize_filename=self.file_sanitize_filename if self.file_sanitize_filename is not None else defaults.sanitize_filename,
            max_filename_length=self.file_max_filename_length or defaults.max_filename_length,
            conflict_strategy=self.file_conflict_strategy or defaults.conflict_strategy,
            encoding=self.file_encoding or defaults.encoding,
        )
    
    def get_default_values(self) -> DefaultValues:
        """获取默认值"""
        defaults = DefaultValues()
        return DefaultValues(
            doc_type=self.default_doc_type or defaults.doc_type,
            count=self.default_count or defaults.count,
            language=self.default_language or defaults.language,
            uniplatform=self.default_uniplatform or defaults.uniplatform,
        )
    
    def get_logging_settings(self) -> LoggingSettings:
        """获取日志设置"""
        defaults = LoggingSettings()
        return LoggingSettings(
            enabled=self.logging_enabled if self.logging_enabled is not None else defaults.enabled,
            level=self.logging_level or defaults.level,
            log_dir=self.logging_log_dir or defaults.log_dir,
            max_log_size=self.logging_max_log_size or defaults.max_log_size,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "download_settings": self.get_download_settings().model_dump(),
            "browser_settings": self.get_browser_settings().model_dump(),
            "file_settings": self.get_file_settings().model_dump(),
            "default_values": self.get_default_values().model_dump(),
            "logging": self.get_logging_settings().model_dump(),
        }


class ConfigWrapper:
    """配置包装类，提供兼容的接口"""
    
    def __init__(self, config: Config):
        self._config = config
    
    @property
    def download(self) -> DownloadSettings:
        return self._config.get_download_settings()
    
    @property
    def browser(self) -> BrowserSettings:
        return self._config.get_browser_settings()
    
    @property
    def file(self) -> FileSettings:
        return self._config.get_file_settings()
    
    @property
    def defaults(self) -> DefaultValues:
        return self._config.get_default_values()
    
    @property
    def logging(self) -> LoggingSettings:
        return self._config.get_logging_settings()


class ConfigManager:
    """配置管理器 - 使用 Pydantic v2 和 .env 文件"""

    DEFAULT_CONFIG_PATH = Path.home() / ".cnki_downloader" / "config.json"

    def __init__(self, config_path: Optional[Path] = None, env_file: Optional[Path] = None):
        """
        初始化配置管理器

        Args:
            config_path: JSON配置文件路径（可选，用于向后兼容）
            env_file: .env 文件路径（默认使用项目根目录的 .env）
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        
        # 加载配置（优先从环境变量/.env，然后从JSON文件）
        # 如果指定了 env_file，使用它；否则尝试项目根目录的 .env
        if env_file:
            env_file_path = Path(env_file)
        else:
            env_file_path = Path(__file__).parent.parent / ".env"
        
        # 创建配置对象（如果 .env 文件存在，会自动加载）
        if env_file_path.exists():
            self.config = Config(_env_file=str(env_file_path))
        else:
            # 如果没有 .env 文件，只从环境变量加载
            self.config = Config()
        
        # 如果JSON配置文件存在，也加载它（用于向后兼容）
        if self.config_path.exists():
            self._load_json_config()

    def _load_json_config(self) -> None:
        """从JSON文件加载配置（向后兼容）"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 更新配置（JSON配置会覆盖环境变量）
                if "download_settings" in data:
                    ds = data["download_settings"]
                    if "default_dir" in ds:
                        self.config.download_default_dir = Path(ds["default_dir"]).expanduser()
                    if "max_concurrent" in ds:
                        self.config.download_max_concurrent = ds["max_concurrent"]
                    if "timeout" in ds:
                        self.config.download_timeout = ds["timeout"]
                    if "retry_times" in ds:
                        self.config.download_retry_times = ds["retry_times"]
                    if "chunk_size" in ds:
                        self.config.download_chunk_size = ds["chunk_size"]
                
                if "browser_settings" in data:
                    bs = data["browser_settings"]
                    if "headless" in bs:
                        self.config.browser_headless = bs["headless"]
                    if "slow_mo" in bs:
                        self.config.browser_slow_mo = bs["slow_mo"]
                    if "user_agent" in bs:
                        self.config.browser_user_agent = bs["user_agent"]
                    if "viewport_width" in bs:
                        self.config.browser_viewport_width = bs["viewport_width"]
                    if "viewport_height" in bs:
                        self.config.browser_viewport_height = bs["viewport_height"]
                    if "locale" in bs:
                        self.config.browser_locale = bs["locale"]
                    if "timezone" in bs:
                        self.config.browser_timezone = bs["timezone"]
                
                if "file_settings" in data:
                    fs = data["file_settings"]
                    if "sanitize_filename" in fs:
                        self.config.file_sanitize_filename = fs["sanitize_filename"]
                    if "max_filename_length" in fs:
                        self.config.file_max_filename_length = fs["max_filename_length"]
                    if "conflict_strategy" in fs:
                        self.config.file_conflict_strategy = fs["conflict_strategy"]
                    if "encoding" in fs:
                        self.config.file_encoding = fs["encoding"]
                
                if "default_values" in data:
                    dv = data["default_values"]
                    if "doc_type" in dv:
                        self.config.default_doc_type = dv["doc_type"]
                    if "count" in dv:
                        self.config.default_count = dv["count"]
                    if "language" in dv:
                        self.config.default_language = dv["language"]
                    if "uniplatform" in dv:
                        self.config.default_uniplatform = dv["uniplatform"]
                
                if "logging" in data:
                    ls = data["logging"]
                    if "enabled" in ls:
                        self.config.logging_enabled = ls["enabled"]
                    if "level" in ls:
                        self.config.logging_level = ls["level"]
                    if "log_dir" in ls:
                        self.config.logging_log_dir = Path(ls["log_dir"]).expanduser()
                    if "max_log_size" in ls:
                        self.config.logging_max_log_size = ls["max_log_size"]
        except Exception as e:
            print(f"⚠️ 加载JSON配置文件失败: {e}，使用环境变量配置")

    def load(self) -> ConfigWrapper:
        """加载配置（兼容旧接口）"""
        return ConfigWrapper(self.config)

    def save(self) -> None:
        """保存配置到JSON文件（用于向后兼容）"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False, default=str)
            print(f"✅ 配置已保存到: {self.config_path}")
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")

    def get(self) -> ConfigWrapper:
        """获取当前配置（返回包装对象以保持兼容性）"""
        return ConfigWrapper(self.config)

    def reset(self) -> None:
        """重置为默认配置"""
        self.config = Config()


# 测试代码
if __name__ == "__main__":
    # 创建配置管理器
    manager = ConfigManager()

    # 获取配置
    config = manager.get()
    print("当前配置:")
    print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False, default=str))

    # 更新配置
    print("\n更新配置...")
    manager.update(max_concurrent=5, headless=True)
    manager.save()

    # 重新加载
    manager2 = ConfigManager()
    config2 = manager2.get()
    print(f"\n并发数: {config2.download.max_concurrent}")
    print(f"无头模式: {config2.browser.headless}")
