"""
格式化工具函数
"""



def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_duration(seconds: float) -> str:
    """格式化时间时长"""
    if seconds < 60:
        return f"{int(seconds)}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}分{secs}秒"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}小时{minutes}分"


def generate_download_report(summary) -> str:
    """生成下载报告"""
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("📊 下载统计:")
    report_lines.append(f"   总计: {summary.total}篇")
    report_lines.append(f"   成功: {summary.success_count}篇")
    report_lines.append(f"   跳过: {summary.skipped_count}篇")
    report_lines.append(f"   失败: {summary.failed_count}篇")

    if summary.files:
        report_lines.append(f"\n📁 保存位置: {summary.request.save_dir}")
        report_lines.append(f"\n📄 下载文件列表 ({len(summary.files)}篇):")
        for i, file_path in enumerate(summary.files, 1):
            report_lines.append(f"   ✅ {file_path.name}")

    if summary.skipped_count > 0 or summary.failed_count > 0:
        report_lines.append(f"\n⚠️ 未成功下载 ({summary.skipped_count + summary.failed_count}篇):")
        for result in summary.results:
            if not result.is_success():
                paper_info = result.paper.title[:50] + "..." if len(result.paper.title) > 50 else result.paper.title
                if result.error_message:
                    report_lines.append(f"   ⚠️ {paper_info} - 原因: {result.error_message}")
                else:
                    report_lines.append(f"   ⚠️ {paper_info}")

    elapsed = summary.get_elapsed_time()
    if elapsed:
        report_lines.append(f"\n⏱️  耗时: {format_duration(elapsed)}")
        speed = summary.get_speed()
        if speed:
            report_lines.append(f"🚀 平均速度: {speed:.1f}篇/分钟")

    report_lines.append("=" * 60)
    return "\n".join(report_lines)
