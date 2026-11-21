"""时间计算核心逻辑：解析、加减、时长格式化和 12 小时制转换。"""

from __future__ import annotations

import re
from typing import Iterable, List, Sequence, Tuple

MINUTES_PER_DAY = 24 * 60
_TIME_PATTERN = re.compile(r"^(\d{1,2}):(\d{2})$")


def _require_int(value: object, name: str) -> int:
    """校验参数必须是整数（排除 bool 和小数）。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("%s 必须是整数" % name)
    return value


def parse_time(text: str) -> int:
    """把 ``HH:MM`` 解析成从 0 点开始的分钟数。"""
    if not isinstance(text, str):
        raise TypeError("时间必须是字符串，例如 07:30")
    cleaned = text.strip()
    match = _TIME_PATTERN.match(cleaned)
    if match is None:
        raise ValueError("时间格式应为 HH:MM，例如 07:30")
    hour = int(match.group(1))
    minute = int(match.group(2))
    if hour > 23:
        raise ValueError("小时应在 0 到 23 之间")
    if minute > 59:
        raise ValueError("分钟应在 0 到 59 之间")
    return hour * 60 + minute


def format_time(minutes: int) -> str:
    """把分钟数格式化成 24 小时制 ``HH:MM``，自动按天循环。"""
    _require_int(minutes, "分钟数")
    hour, minute = divmod(minutes % MINUTES_PER_DAY, 60)
    return "%02d:%02d" % (hour, minute)


def add_minutes(text: str, delta: int) -> str:
    """在给定时刻上增加分钟数，结果按 24 小时循环。"""
    _require_int(delta, "增量")
    return format_time(parse_time(text) + delta)


def elapsed(start: str, end: str, next_day: bool = True) -> int:
    """计算两个时刻之间的分钟数，默认把跨零点视为第二天。"""
    begin = parse_time(start)
    finish = parse_time(end)
    if finish < begin:
        if not next_day:
            raise ValueError("结束时刻早于开始时刻，请检查是否跨天")
        finish += MINUTES_PER_DAY
    return finish - begin


def format_duration(minutes: int) -> str:
    """把分钟数格式化成中文时长，例如 ``2 小时 30 分钟``。"""
    _require_int(minutes, "时长")
    if minutes < 0:
        raise ValueError("时长不能为负数")
    hours, rest = divmod(minutes, 60)
    if hours and rest:
        return "%d 小时 %d 分钟" % (hours, rest)
    if hours:
        return "%d 小时" % hours
    return "%d 分钟" % rest


def _day_part(hour: int) -> str:
    if hour < 5:
        return "凌晨"
    if hour < 8:
        return "早上"
    if hour < 12:
        return "上午"
    if hour == 12:
        return "中午"
    if hour < 18:
        return "下午"
    return "晚上"


def to_12hour(text: str) -> str:
    """转换成口语化的 12 小时制，例如 ``下午 1:05``。"""
    minutes = parse_time(text)
    hour, minute = divmod(minutes, 60)
    display = 12 if hour == 12 else (0 if hour == 0 else hour % 12)
    return "%s %d:%02d" % (_day_part(hour), display, minute)


def schedule(start: str, durations: Sequence[int]) -> List[Tuple[str, str]]:
    """根据一节课的时长列表，生成连续的 (开始, 结束) 时刻。"""
    if not durations:
        raise ValueError("至少需要一个时长")
    current = parse_time(start)
    blocks: List[Tuple[str, str]] = []
    for duration in durations:
        _require_int(duration, "每节时长")
        if duration <= 0:
            raise ValueError("每节时长必须大于 0")
        finish = current + duration
        blocks.append((format_time(current), format_time(finish)))
        current = finish
    return blocks


def total_minutes(durations: Iterable[int]) -> int:
    """汇总多个时长，空列表返回 0。"""
    total = 0
    for duration in durations:
        _require_int(duration, "每节时长")
        if duration < 0:
            raise ValueError("时长不能为负数")
        total += duration
    return total
