"""timecalc 渲染测试。"""

import unittest

from timecalc.render import schedule_table, timeline_svg, worksheet_html

BLOCKS = [("语文", "08:00", "08:40"), ("数学", "08:50", "09:30")]


class TimelineTests(unittest.TestCase):
    def test_contains_svg(self):
        svg = timeline_svg(BLOCKS)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))

    def test_contains_labels(self):
        svg = timeline_svg(BLOCKS)
        self.assertIn("语文", svg)
        self.assertIn("数学", svg)

    def test_contains_hour_grid(self):
        svg = timeline_svg(BLOCKS)
        self.assertIn("00:00", svg)
        self.assertIn("12:00", svg)

    def test_contains_time_range(self):
        svg = timeline_svg(BLOCKS)
        self.assertIn("08:00-08:40", svg)

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            timeline_svg([])

    def test_escapes_html(self):
        svg = timeline_svg([("<script>", "08:00", "08:40")])
        self.assertNotIn("<script>", svg)
        self.assertIn("&lt;script&gt;", svg)

    def test_cross_midnight_block(self):
        svg = timeline_svg([("晚自习", "23:40", "00:20")])
        self.assertIn("23:40", svg)


class TableTests(unittest.TestCase):
    def test_contains_header(self):
        table = schedule_table(BLOCKS)
        self.assertIn("<table>", table)
        self.assertIn("开始", table)

    def test_contains_duration(self):
        table = schedule_table(BLOCKS)
        self.assertIn("40 分钟", table)

    def test_contains_index(self):
        table = schedule_table(BLOCKS)
        self.assertIn("1. 语文", table)
        self.assertIn("2. 数学", table)

    def test_escapes_label(self):
        table = schedule_table([("<b>", "08:00", "08:30")])
        self.assertNotIn("<b>", table)

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            schedule_table([])


class WorksheetTests(unittest.TestCase):
    def test_is_full_document(self):
        page = worksheet_html("课程表", BLOCKS)
        self.assertTrue(page.startswith("<!DOCTYPE html>"))
        self.assertIn("</html>", page)

    def test_contains_title(self):
        page = worksheet_html("三年级课程表", BLOCKS)
        self.assertIn("三年级课程表", page)

    def test_contains_timeline(self):
        page = worksheet_html("课程表", BLOCKS)
        self.assertIn("<svg", page)

    def test_contains_footer(self):
        page = worksheet_html("课程表", BLOCKS)
        self.assertIn("timecalc", page)

    def test_escapes_title(self):
        page = worksheet_html("<i>课</i>", BLOCKS)
        self.assertNotIn("<i>", page)


if __name__ == "__main__":
    unittest.main()
