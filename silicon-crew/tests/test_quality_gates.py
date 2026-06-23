from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


DOC = load("check_doc_completeness")
RTL = load("check_rtl_quality")
SIM = load("check_sim_pass")
TIMING = load("check_timing")


class QualityGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_doc_requires_all_nonempty_documents(self) -> None:
        docs = self.root / "docs"
        docs.mkdir()
        for filename in DOC.REQUIRED_DOCS:
            (docs / filename).write_text(f"# {filename}\ncontent\n")
        self.assertTrue(DOC.check(str(self.root))["passed"])
        (docs / "verification_plan.md").write_text("")
        self.assertFalse(DOC.check(str(self.root))["passed"])

    def test_rtl_uses_canonical_filelist(self) -> None:
        project = self.root / "soc"
        module = project / "ip" / "digital" / "demo"
        (project / "chip").mkdir(parents=True)
        rtl = module / "de" / "rtl"
        rtl.mkdir(parents=True)
        source = rtl / "demo.v"
        source.write_text("module demo(input wire a, output wire y); assign y = a; endmodule\n")
        (rtl / "filelist.f").write_text("$SOC/ip/digital/demo/de/rtl/demo.v\n")
        with patch.dict(os.environ, {"SOC": str(project)}):
            result = RTL.check(str(module), "demo")
        self.assertTrue(result["passed"], result)

    def test_sim_rejects_real_error_without_sentinel_workaround(self) -> None:
        sim = self.root / "dv" / "sim"
        sim.mkdir(parents=True)
        log = sim / "sim.log"
        log.write_text("Test summary: PASS=3 ERROR=0\nRESULT: ALL TESTS PASS\n")
        self.assertTrue(SIM.check(str(self.root), ["dv/sim/sim.log"])["passed"])
        log.write_text("[ERROR] mismatch at cycle 4\nRESULT: ALL TESTS PASS\n")
        self.assertFalse(SIM.check(str(self.root), ["dv/sim/sim.log"])["passed"])

    def test_timing_rejects_estimates(self) -> None:
        syn = self.root / "de" / "syn"
        syn.mkdir(parents=True)
        report = syn / "timing.rpt"
        report.write_text("Estimated generic timing\nWNS = 1.0\nTNS = 0.0\n")
        self.assertFalse(TIMING.check(str(self.root))["passed"])
        report.write_text("STA_TOOL: opensta\nWNS = 1.0\nTNS = 0.0\n")
        self.assertTrue(TIMING.check(str(self.root))["passed"])


if __name__ == "__main__":
    unittest.main()
