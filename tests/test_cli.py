"""timecalc 命令行测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from timecalc.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class AddCommandTests(unittest.TestCase):
    def test_add_output(self):
        code, out, _ = run(["add", "07:30", "45"])
        self.assertEqual(code, 0)
        self.assertIn("08:15", out)

    def test_add_negative(self):
        code, out, _ = run(["add", "00:10", "-20"])
        self.assertEqual(code, 0)
        self.assertIn("23:50", out)

    def test_add_invalid_time(self):
        code, _, err = run(["add", "7点", "10"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class DiffCommandTests(unittest.TestCase):
    def test_diff_output(self):
        code, out, _ = run(["diff", "08:15", "11:45"])
        self.assertEqual(code, 0)
        self.assertIn("210", out)
        self.assertIn("3 小时 30 分钟", out)

    def test_diff_cross_midnight(self):
        code, out, _ = run(["diff", "23:30", "00:30"])
        self.assertEqual(code, 0)
        self.assertIn("60", out)


class DurationCommandTests(unittest.TestCase):
    def test_duration_output(self):
        code, out, _ = run(["duration", "150"])
        self.assertEqual(code, 0)
        self.assertIn("2 小时 30 分钟", out)

    def test_duration_negative(self):
        code, _, err = run(["duration", "-5"])
        self.assertEqual(code, 2)
        self.assertIn("不能为负数", err)


class H12CommandTests(unittest.TestCase):
    def test_h12_output(self):
        code, out, _ = run(["h12", "13:05"])
        self.assertEqual(code, 0)
        self.assertIn("下午 1:05", out)

    def test_h12_invalid(self):
        code, _, err = run(["h12", "25:00"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class ScheduleCommandTests(unittest.TestCase):
    def test_schedule_output(self):
        code, out, _ = run(["schedule", "08:00", "40", "10", "40"])
        self.assertEqual(code, 0)
        self.assertIn("第 1 节 08:00-08:40", out)
        self.assertIn("第 3 节 08:50-09:30", out)

    def test_schedule_total(self):
        _, out, _ = run(["schedule", "08:00", "40", "10", "40"])
        self.assertIn("共 90 分钟", out)

    def test_schedule_rejects_zero(self):
        code, _, err = run(["schedule", "08:00", "0"])
        self.assertEqual(code, 2)
        self.assertIn("大于 0", err)


class SheetCommandTests(unittest.TestCase):
    def test_sheet_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sheet.html"
            code, out, _ = run(
                ["sheet", "08:00", "40", "40", "-o", str(output)]
            )
            self.assertEqual(code, 0)
            self.assertTrue(output.exists())
            self.assertIn("已生成课表", out)

    def test_sheet_contains_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sheet.html"
            run(["sheet", "08:00", "40", "-o", str(output)])
            text = output.read_text(encoding="utf-8")
            self.assertIn("<svg", text)

    def test_sheet_custom_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sheet.html"
            run(["sheet", "08:00", "40", "-o", str(output), "--title", "期末复习"])
            self.assertIn("期末复习", output.read_text(encoding="utf-8"))

    def test_sheet_missing_output(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stderr(io.StringIO()):
                main(["sheet", "08:00", "40"])
        self.assertEqual(ctx.exception.code, 2)


class ParserTests(unittest.TestCase):
    def test_help_exits_zero(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stdout(io.StringIO()):
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_unknown_command(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stderr(io.StringIO()):
                main(["unknown"])
        self.assertEqual(ctx.exception.code, 2)

    def test_no_command(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stderr(io.StringIO()):
                main([])
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
