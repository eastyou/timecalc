# timecalc

[![CI](https://github.com/eastyou/timecalc/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/timecalc/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

面向课堂与生活的时间计算工具：时刻加减、跨零点时长、12 小时制转换和可打印课表。

## 功能

- `HH:MM` 严格解析，小时、分钟越界都会给出中文错误提示
- 时刻加减分钟，自动按 24 小时循环
- 计算两个时刻的间隔，默认把跨零点视为第二天
- 把分钟数格式化为「2 小时 30 分钟」
- 转换成「早上 7:30」「下午 1:05」等口语表达
- 按每节时长自动排出连续课表
- 生成含 SVG 时间轴与明细表的单文件 HTML

## 安装

```bash
pip install -e .
```

也可以不安装，直接在仓库根目录运行 `python -m timecalc`。

## 使用

```bash
# 时刻加减
timecalc add 07:30 45          # 07:30 +45 分钟 = 08:15
timecalc add 00:10 -20         # 00:10 -20 分钟 = 23:50

# 两个时刻的间隔
timecalc diff 08:15 11:45      # 共 210 分钟（3 小时 30 分钟）
timecalc diff 23:30 00:30      # 跨零点，共 60 分钟

# 时长格式化
timecalc duration 150          # 150 分钟 = 2 小时 30 分钟

# 12 小时制
timecalc h12 13:05             # 13:05 → 下午 1:05

# 排课表
timecalc schedule 08:00 40 10 40

# 生成可打印课表
timecalc sheet 08:00 40 10 40 40 10 40 -o examples/sheet.html --title "三年级课程表"
```

## 作为库使用

```python
from timecalc import add_minutes, elapsed, schedule, to_12hour

assert add_minutes("07:30", 45) == "08:15"
assert elapsed("23:30", "00:30") == 60
assert to_12hour("13:05") == "下午 1:05"
assert schedule("08:00", [40, 10, 40])[2] == ("08:50", "09:30")
```

## 示例

[examples/sheet.html](examples/sheet.html) 是生成的课程表页面，包含时间轴、明细表和打印样式。

## 测试

```bash
python -m unittest discover -s tests -v
```

共 82 项单元测试，覆盖解析、加减、跨零点、12 小时制、排课、渲染和命令行错误处理。CI 在 Linux、macOS、Windows 上运行 Python 3.9 ~ 3.13。

## 许可

MIT © 2026 eastyou
