"""timecalc：面向课堂与生活的时间计算小工具。"""

from .model import (
    add_minutes,
    elapsed,
    format_duration,
    format_time,
    parse_time,
    schedule,
    to_12hour,
    total_minutes,
)
from .render import schedule_table, timeline_svg, worksheet_html

__all__ = [
    "add_minutes",
    "elapsed",
    "format_duration",
    "format_time",
    "parse_time",
    "schedule",
    "to_12hour",
    "total_minutes",
    "schedule_table",
    "timeline_svg",
    "worksheet_html",
]

__version__ = "0.1.0"
