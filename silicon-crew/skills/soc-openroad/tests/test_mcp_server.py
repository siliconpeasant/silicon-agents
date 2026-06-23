from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SERVER_PATH = ROOT / "skills/soc-openroad/mcp_server.py"
SPEC = importlib.util.spec_from_file_location("soc_openroad_mcp_server_test", SERVER_PATH)
SERVER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(SERVER)


class SocOpenroadServerTest(unittest.TestCase):
    def test_init_generates_portable_orfs_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "demo"
            self._write_module(project, "chip/core", "core")
            self._write_module(project, "chip/bus", "bus")
            self._write_module(project, "chip/top", "demo_top")
            top_mk = project / "chip/top/de/rtl/filelist.mk"
            top_mk.write_text(
                "\n".join(
                    [
                        "include $(PROJECT_ROOT)/chip/core/de/rtl/filelist.mk",
                        "include $(PROJECT_ROOT)/chip/bus/de/rtl/filelist.mk",
                    ]
                )
                + "\n"
            )

            result = SERVER.soc_openroad_init(
                str(project),
                module_dir="chip/top",
                design_name="demo_top",
                top_module="demo_top",
                platform="nangate45",
                clock_period_ns=5.0,
            )

            self.assertIn("[OK] OpenROAD config generated", result)
            config = project / "pd/openroad/nangate45/demo_top/config.mk"
            sdc = project / "pd/openroad/nangate45/demo_top/constraint.sdc"
            self.assertTrue(config.is_file())
            self.assertTrue(sdc.is_file())
            text = config.read_text()
            self.assertIn("export DESIGN_NAME = demo_top", text)
            self.assertIn("$(PROJECT_ROOT)/chip/core/de/rtl/core.v", text)
            self.assertIn("$(PROJECT_ROOT)/chip/bus/de/rtl/bus.v", text)
            self.assertIn("$(PROJECT_ROOT)/chip/top/de/rtl/demo_top.v", text)
            self.assertNotIn(str(project), text)
            self.assertIn("set clk_period 5", sdc.read_text())

    def test_status_reports_missing_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            status = SERVER.soc_openroad_status(tmp, design_name="demo_top")
            self.assertIn('"synth"', status)
            self.assertIn('"exists": false', status)

    def _write_module(self, project: Path, relative: str, name: str) -> None:
        rtl = project / relative / "de/rtl"
        rtl.mkdir(parents=True)
        (rtl / f"{name}.v").write_text(f"module {name}(input clk); endmodule\n")
        (rtl / "filelist.f").write_text(f"$SOC/{relative}/de/rtl/{name}.v\n")
        (rtl / "filelist.mk").write_text("# unit test filelist\n")


if __name__ == "__main__":
    unittest.main()
