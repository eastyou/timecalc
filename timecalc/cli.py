"""timecalc 命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from .model import (
    add_minutes,
    elapsed,
    format_duration,
    format_time,
    schedule,
    to_12hour,
    total_minutes,
)
from .render import worksheet_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="timecalc", description="时间计算：时刻加减、时长统计与课表生成"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="在时刻上加减分钟")
    add.add_argument("time", help="开始时刻，例如 07:30")
    add.add_argument("delta", type=int, help="分钟数，可为负数")

    diff = sub.add_parser("diff", help="计算两个时刻的间隔")
    diff.add_argument("start", help="开始时刻")
    diff.add_argument("end", help="结束时刻")

    duration = sub.add_parser("duration", help="把分钟数格式化成时长")
    duration.add_argument("minutes", type=int, help="分钟数")

    h12 = sub.add_parser("h12", help="转换为 12 小时制")
    h12.add_argument("time", help="24 小时制时刻")

    sched = sub.add_parser("schedule", help="按每节时长排出连续时刻")
    sched.add_argument("start", help="第一节课开始时刻")
    sched.add_argument("durations", nargs="+", type=int, help="每节时长（分钟）")

    sheet = sub.add_parser("sheet", help="生成可打印的 HTML 课表")
    sheet.add_argument("start", help="第一节课开始时刻")
    sheet.add_argument("durations", nargs="+", type=int, help="每节时长（分钟）")
    sheet.add_argument("-o", "--output", required=True, help="输出 HTML 路径")
    sheet.add_argument("--title", default="我的课程表", help="页面标题")

    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "add":
        print("%s %+d 分钟 = %s" % (args.time, args.delta, add_minutes(args.time, args.delta)))
        return 0
    if args.command == "diff":
        minutes = elapsed(args.start, args.end)
        print(
            "%s → %s 共 %d 分钟（%s）"
            % (args.start, args.end, minutes, format_duration(minutes))
        )
        return 0
    if args.command == "duration":
        print("%d 分钟 = %s" % (args.minutes, format_duration(args.minutes)))
        return 0
    if args.command == "h12":
        print("%s → %s" % (args.time, to_12hour(args.time)))
        return 0
    if args.command == "schedule":
        blocks = schedule(args.start, args.durations)
        for index, (begin, end) in enumerate(blocks, start=1):
            print("第 %d 节 %s-%s" % (index, begin, end))
        print("共 %d 分钟（%s）" % (total_minutes(args.durations), format_duration(total_minutes(args.durations))))
        return 0
    if args.command == "sheet":
        blocks = schedule(args.start, args.durations)
        rows = [("第 %d 节" % i, b, e) for i, (b, e) in enumerate(blocks, start=1)]
        output = Path(args.output)
        output.write_text(worksheet_html(args.title, rows), encoding="utf-8")
        print("已生成课表：%s" % output)
        return 0
    raise ValueError("未知命令：%s" % args.command)


def _ensure_utf8_console() -> None:
    """Windows 控制台默认编码可能无法输出中文，尽量切换为 UTF-8。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            continue


def main(argv: Optional[Sequence[str]] = None) -> int:
    _ensure_utf8_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (TypeError, ValueError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
