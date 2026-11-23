"""Offline unit tests for obi_gv.py. Run: python3 -m unittest discover -s tests -v

No device or network is needed; HTTP is stubbed.
"""
import contextlib
import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "obi-gv-revival" / "scripts"))
import obi_gv as o  # noqa: E402

DI_XML = """<model><object name="Product Information"><parameter name="ModelName"><value hash="1" current="OBi200" default="OBi100"></value></parameter>
<parameter name="HardwareVersion"><value hash="2" current="1.4" default=""></value></parameter>
<parameter name="SoftwareVersion"><value hash="3" current="3.2.2 (Build: 8680EX-arrynrob13)" default=""></value></parameter>
<parameter name="UpTime"><value hash="4" current=" 0 Days  1:02:03    (2)" default=""></value></parameter></object>
<object name="SP1 Service Status"><parameter name="Status"><value hash="5" current="Connected" default=""></value></parameter></object></model>"""


class FakeObi(o.Obi):
    def __init__(self, pages=None, dry_run=True):
        super().__init__("192.0.2.1", "admin", "pw", dry_run)
        self.pages = pages or {}

    def get(self, path, timeout=20):
        return self.pages[path]


class RouteTests(unittest.TestCase):
    def test_routes(self):
        cases = {
            "3.2.2 (Build: 8680EX)": ["stock5921", "bypass", "arrynrob13"],
            "3.2.2 (Build: 7628)": ["stock5921", "bypass", "arrynrob13"],
            "3.2.2 (Build: 5921EX)": ["bypass", "arrynrob13"],
            "3.2.2 (Build: 5898EX)": ["bypass", "arrynrob13"],
            "3.2.2 (Build: 5757EX)": ["arrynrob13"],
            "3.2.2 (Build: 5921EX-arrynrob9)": ["arrynrob13"],
            "3.2.2 (Build: 8680EX-arrynrob13)": [],
        }
        for ver, route in cases.items():
            self.assertEqual(o.plan_route(ver), route, ver)

    def test_6259_is_ambiguous(self):
        v = "3.2.2 (Build: 6259)"
        with self.assertRaises(o.ObiError):
            o.plan_route(v)
        self.assertEqual(o.plan_route(v, bypass_installed=True), ["arrynrob13"])
        self.assertEqual(o.plan_route(v, stock_6259=True), ["stock5921", "bypass", "arrynrob13"])

    def test_bypass_never_flashed_from_6259_or_higher(self):
        for ver in ("3.2.2 (Build: 6259)", "3.2.2 (Build: 8680EX)", "3.2.2 (Build: 7628)"):
            self.assertFalse(o.step_allowed("bypass", ver, False), ver)
        self.assertTrue(o.step_allowed("bypass", "3.2.2 (Build: 5921EX)", False))

    def test_arrynrob_gate(self):
        self.assertFalse(o.step_allowed("arrynrob13", "3.2.2 (Build: 8680EX)", False))
        self.assertFalse(o.step_allowed("arrynrob13", "3.2.2 (Build: 6259)", False))
        self.assertTrue(o.step_allowed("arrynrob13", "3.2.2 (Build: 6259)", True))
        self.assertTrue(o.step_allowed("arrynrob13", "3.2.2 (Build: 5921EX)", False))


class DeviceTests(unittest.TestCase):
    def test_device_info_and_support(self):
        info = o.device_info(FakeObi({"DI_S_.xml": DI_XML}))
        self.assertEqual(info["model"], "OBi200")
        self.assertEqual(info["uptime_s"], 3723)
        self.assertEqual(info["sp"][1], "Connected")
        o.require_supported(info)

    def test_unsupported_model_refused(self):
        with self.assertRaises(o.ObiError):
            o.require_supported({"model": "OBi110", "version": "1.3.0 (Build: 2886)"})

    def test_parse_params_uses_default_when_no_current(self):
        xml = '<object name="A"><parameter name="P"><value hash="h1" default="d"></value></parameter></object>'
        self.assertEqual(o.parse_params(xml)[("A", "P")], ("h1", "d", "d"))
        with self.assertRaises(o.ObiError):
            o.find({}, "A", "P")


class SafetyTests(unittest.TestCase):
    def test_token_masked_in_dry_run(self):
        secret = "1//SECRET-TOKEN-VALUE-0123456789"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            FakeObi().set_params([("abc123", secret), ("def456", "x")], mask=("abc123",))
        self.assertNotIn(secret, buf.getvalue())
        self.assertIn("****", buf.getvalue())

    def test_cfg_quote_escapes(self):
        self.assertEqual(o.cfg_quote('a"b\\c'), '"a\\"b\\\\c"')

    def test_checksum_gate(self):
        with tempfile.TemporaryDirectory() as d:
            data = b"fake firmware"
            (Path(d) / "x.fw").write_bytes(data)
            good = hashlib.sha256(data).hexdigest()
            saved = dict(o.FIRMWARE)
            try:
                o.FIRMWARE["t"] = ("x.fw", good, "v", "https://example.invalid/x.fw")
                self.assertEqual(o.firmware_path(d, "t").name, "x.fw")
                o.FIRMWARE["t"] = ("x.fw", "0" * 64, "v", "https://example.invalid/x.fw")
                with self.assertRaises(o.ObiError):
                    o.firmware_path(d, "t")
                o.FIRMWARE["t"] = ("missing.fw", good, "v", "https://example.invalid/m.fw")
                with self.assertRaises(o.ObiError) as cm:
                    o.firmware_path(d, "t")
                self.assertIn("example.invalid", str(cm.exception))
            finally:
                o.FIRMWARE.clear()
                o.FIRMWARE.update(saved)

    def test_backup_refused_inside_skill_folder(self):
        self.assertTrue(o.inside_git_repo(o.HERE))
        self.assertTrue(o.inside_git_repo(o.HERE.parent / "backup"))

    def test_firmware_table_complete(self):
        for name, (fname, sha, expect, url) in o.FIRMWARE.items():
            self.assertTrue(fname.endswith(".fw"))
            self.assertEqual(len(sha), 64)
            self.assertTrue(url.startswith("https://"))


if __name__ == "__main__":
    unittest.main()
