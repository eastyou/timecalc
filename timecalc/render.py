"""把日程渲染成 SVG 时间轴和可打印的 HTML 课表。"""

from __future__ import annotations

import html
from typing import Sequence, Tuple

from .model import MINUTES_PER_DAY, parse_time

PALETTE = ("#2563eb", "#0ea5e9", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6")
CHART_WIDTH = 520
LABEL_WIDTH = 150
ROW_HEIGHT = 44


def _safe(text: object) -> str:
    return html.escape(str(text), quote=True)


def _block_bounds(block: Tuple[str, str, str]) -> Tuple[str, int, int]:
    label, start, end = block
    begin = parse_time(start)
    finish = parse_time(end)
    if finish <= begin:
        finish += MINUTES_PER_DAY
    finish = min(finish, MINUTES_PER_DAY)
    return label, begin, finish


def timeline_svg(blocks: Sequence[Tuple[str, str, str]]) -> str:
    """绘制横向时间轴，每个块包含标题、开始和结束时刻。"""
    if not blocks:
        raise ValueError("至少需要一个日程块")
    height = 46 + ROW_HEIGHT * len(blocks)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 %d" '
        'role="img" aria-label="日程时间轴">' % height,
        '<rect width="720" height="%d" fill="#f8fafc"/>' % height,
    ]
    for hour in range(0, 25, 3):
        x = LABEL_WIDTH + CHART_WIDTH * hour / 24.0
        parts.append(
            '<line x1="%.1f" y1="24" x2="%.1f" y2="%d" stroke="#e2e8f0"/>'
            % (x, x, height - 8)
        )
        parts.append(
            '<text x="%.1f" y="18" font-size="11" fill="#64748b" '
            'text-anchor="middle">%02d:00</text>' % (x, hour % 24)
        )
    for index, block in enumerate(blocks):
        label, begin, finish = _block_bounds(block)
        y = 34 + index * ROW_HEIGHT
        x1 = LABEL_WIDTH + CHART_WIDTH * begin / float(MINUTES_PER_DAY)
        width = max(4.0, CHART_WIDTH * (finish - begin) / float(MINUTES_PER_DAY))
        color = PALETTE[index % len(PALETTE)]
        parts.append(
            '<text x="8" y="%d" font-size="13" fill="#0f172a">%s</text>'
            % (y + 16, _safe(label))
        )
        parts.append(
            '<rect x="%.1f" y="%d" width="%.1f" height="26" rx="6" fill="%s" '
            'opacity="0.88"/>' % (x1, y, width, color)
        )
        parts.append(
            '<text x="%.1f" y="%d" font-size="11" fill="#ffffff">%s-%s</text>'
            % (x1 + 5, y + 18, _safe(block[1]), _safe(block[2]))
        )
    parts.append("</svg>")
    return "\n".join(parts)


def schedule_table(blocks: Sequence[Tuple[str, str, str]]) -> str:
    """生成日程明细表。"""
    if not blocks:
        raise ValueError("至少需要一个日程块")
    rows = ["<table><thead><tr><th>节次</th><th>开始</th><th>结束</th><th>用时</th></tr></thead><tbody>"]
    for index, block in enumerate(blocks, start=1):
        label, start, end = block
        _, begin, finish = _block_bounds(block)
        rows.append(
            "<tr><td>%d. %s</td><td>%s</td><td>%s</td><td>%d 分钟</td></tr>"
            % (index, _safe(label), _safe(start), _safe(end), finish - begin)
        )
    rows.append("</tbody></table>")
    return "\n".join(rows)


def worksheet_html(title: str, blocks: Sequence[Tuple[str, str, str]]) -> str:
    """输出可直接打印的完整 HTML 页面。"""
    safe_title = _safe(title or "我的日程")
    return (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>%s</title>\n<style>\n"
        "body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;"
        "background:#eef2ff;margin:0;padding:24px;color:#0f172a}\n"
        ".card{max-width:780px;margin:0 auto;background:#fff;border-radius:16px;"
        "padding:24px;box-shadow:0 12px 30px rgba(15,23,42,.12)}\n"
        "h1{font-size:22px;margin:0 0 16px}\n"
        "table{width:100%%;border-collapse:collapse;margin-top:18px;font-size:14px}\n"
        "th,td{border-bottom:1px solid #e2e8f0;padding:8px;text-align:left}\n"
        "th{background:#f1f5f9}\n"
        "footer{margin-top:16px;font-size:12px;color:#64748b}\n"
        "</style>\n</head>\n<body>\n<div class=\"card\">\n<h1>%s</h1>\n"
        "%s\n%s\n<footer>由 timecalc 生成 · Python 标准库</footer>\n</div>\n</body>\n</html>"
        % (
            safe_title,
            safe_title,
            timeline_svg(blocks),
            schedule_table(blocks),
        )
    )
