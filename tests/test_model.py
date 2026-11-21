"""timecalc 核心逻辑测试。"""

import unittest

from timecalc.model import (
    add_minutes,
    elapsed,
    format_duration,
    format_time,
    parse_time,
    schedule,
    to_12hour,
    total_minutes,
)


class ParseTimeTests(unittest.TestCase):
    def test_parse_standard(self):
        self.assertEqual(parse_time("07:30"), 450)

    def test_parse_single_digit_hour(self):
        self.assertEqual(parse_time("7:05"), 425)

    def test_parse_midnight(self):
        self.assertEqual(parse_time("00:00"), 0)

    def test_parse_last_minute(self):
        self.assertEqual(parse_time("23:59"), 1439)

    def test_parse_strips_spaces(self):
        self.assertEqual(parse_time("  12:00  "), 720)

    def test_parse_rejects_bad_format(self):
        for value in ("7点30", "0730", "07:3", "07:300", "", "ab:cd"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_time(value)

    def test_parse_rejects_out_of_range_hour(self):
        with self.assertRaises(ValueError):
            parse_time("24:00")

    def test_parse_rejects_out_of_range_minute(self):
        with self.assertRaises(ValueError):
            parse_time("12:60")

    def test_parse_rejects_non_string(self):
        with self.assertRaises(TypeError):
            parse_time(730)  # type: ignore[arg-type]


class FormatTimeTests(unittest.TestCase):
    def test_format_basic(self):
        self.assertEqual(format_time(450), "07:30")

    def test_format_pads_zero(self):
        self.assertEqual(format_time(5), "00:05")

    def test_format_wraps_forward(self):
        self.assertEqual(format_time(1440), "00:00")

    def test_format_wraps_backward(self):
        self.assertEqual(format_time(-30), "23:30")

    def test_format_rejects_float(self):
        with self.assertRaises(TypeError):
            format_time(12.5)  # type: ignore[arg-type]

    def test_format_rejects_bool(self):
        with self.assertRaises(TypeError):
            format_time(True)  # type: ignore[arg-type]


class AddMinutesTests(unittest.TestCase):
    def test_add_forward(self):
        self.assertEqual(add_minutes("07:30", 45), "08:15")

    def test_add_backward_wrap(self):
        self.assertEqual(add_minutes("00:10", -20), "23:50")

    def test_add_zero(self):
        self.assertEqual(add_minutes("09:00", 0), "09:00")

    def test_add_big_delta(self):
        self.assertEqual(add_minutes("09:00", 1441), "09:01")

    def test_add_rejects_float_delta(self):
        with self.assertRaises(TypeError):
            add_minutes("09:00", 1.5)  # type: ignore[arg-type]


class ElapsedTests(unittest.TestCase):
    def test_elapsed_same_day(self):
        self.assertEqual(elapsed("08:15", "11:45"), 210)

    def test_elapsed_cross_midnight(self):
        self.assertEqual(elapsed("23:30", "00:30"), 60)

    def test_elapsed_same_time(self):
        self.assertEqual(elapsed("10:00", "10:00"), 0)

    def test_elapsed_next_day_disabled(self):
        with self.assertRaises(ValueError):
            elapsed("23:30", "00:30", next_day=False)

    def test_elapsed_rejects_bad_time(self):
        with self.assertRaises(ValueError):
            elapsed("8点", "09:00")


class DurationTests(unittest.TestCase):
    def test_duration_hours_minutes(self):
        self.assertEqual(format_duration(150), "2 小时 30 分钟")

    def test_duration_exact_hours(self):
        self.assertEqual(format_duration(120), "2 小时")

    def test_duration_minutes_only(self):
        self.assertEqual(format_duration(45), "45 分钟")

    def test_duration_zero(self):
        self.assertEqual(format_duration(0), "0 分钟")

    def test_duration_negative(self):
        with self.assertRaises(ValueError):
            format_duration(-1)

    def test_duration_rejects_bool(self):
        with self.assertRaises(TypeError):
            format_duration(False)  # type: ignore[arg-type]


class To12HourTests(unittest.TestCase):
    def test_morning_early(self):
        self.assertEqual(to_12hour("06:30"), "早上 6:30")

    def test_morning(self):
        self.assertEqual(to_12hour("09:05"), "上午 9:05")

    def test_noon(self):
        self.assertEqual(to_12hour("12:00"), "中午 12:00")

    def test_afternoon(self):
        self.assertEqual(to_12hour("13:05"), "下午 1:05")

    def test_evening(self):
        self.assertEqual(to_12hour("18:00"), "晚上 6:00")

    def test_midnight(self):
        self.assertEqual(to_12hour("00:10"), "凌晨 0:10")


class ScheduleTests(unittest.TestCase):
    def test_schedule_simple(self):
        self.assertEqual(schedule("08:00", [40]), [("08:00", "08:40")])

    def test_schedule_accumulates(self):
        self.assertEqual(
            schedule("08:00", [40, 10, 40]),
            [("08:00", "08:40"), ("08:40", "08:50"), ("08:50", "09:30")],
        )

    def test_schedule_rejects_empty(self):
        with self.assertRaises(ValueError):
            schedule("08:00", [])

    def test_schedule_rejects_nonpositive(self):
        with self.assertRaises(ValueError):
            schedule("08:00", [40, 0])

    def test_schedule_rejects_float(self):
        with self.assertRaises(TypeError):
            schedule("08:00", [40.5])  # type: ignore[list-item]

    def test_schedule_crosses_midnight(self):
        self.assertEqual(schedule("23:40", [40]), [("23:40", "00:20")])


class TotalMinutesTests(unittest.TestCase):
    def test_total_minutes(self):
        self.assertEqual(total_minutes([40, 10, 40]), 90)

    def test_total_minutes_empty(self):
        self.assertEqual(total_minutes([]), 0)

    def test_total_minutes_rejects_negative(self):
        with self.assertRaises(ValueError):
            total_minutes([10, -5])


if __name__ == "__main__":
    unittest.main()
