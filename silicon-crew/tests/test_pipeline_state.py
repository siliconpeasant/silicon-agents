from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import init_state
import update_state


class PipelineStateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name) / "demo"
        init_state.init_state_single(str(self.workspace), "demo")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def state(self) -> dict:
        return json.loads((self.workspace / "pipeline_state.json").read_text())

    def test_initial_state_dispatches_doc_only(self) -> None:
        state = self.state()
        self.assertEqual(state["pipeline"]["doc"]["status"], "pending")
        self.assertEqual(state["pipeline"]["rtl"]["status"], "blocked")
        self.assertEqual([item["stage"] for item in state["next_actions"]], ["doc"])

    def test_done_requires_in_progress_artifact_and_checks(self) -> None:
        artifact = self.workspace / "docs" / "design_spec.md"
        artifact.parent.mkdir()
        artifact.write_text("# Design\n")
        with self.assertRaisesRegex(ValueError, "invalid transition"):
            update_state.update_state(
                str(self.workspace),
                "doc",
                "done",
                artifacts=["docs/design_spec.md"],
                checks=["doc:passed"],
            )
        update_state.update_state(str(self.workspace), "doc", "in_progress")
        with self.assertRaisesRegex(ValueError, "does not exist"):
            update_state.update_state(
                str(self.workspace),
                "doc",
                "done",
                artifacts=["docs/missing.md"],
                checks=["doc:passed"],
            )

    def test_multiple_checks_are_preserved_and_unblock_rtl(self) -> None:
        artifact = self.workspace / "docs" / "design_spec.md"
        artifact.parent.mkdir()
        artifact.write_text("# Design\n")
        update_state.update_state(str(self.workspace), "doc", "in_progress")
        update_state.update_state(
            str(self.workspace),
            "doc",
            "done",
            artifacts=["docs/design_spec.md"],
            checks=["doc:passed", "review:passed:approved"],
        )
        state = self.state()
        self.assertEqual(len(state["pipeline"]["doc"]["check_results"]), 2)
        self.assertEqual(state["pipeline"]["rtl"]["status"], "pending")

    def test_only_doc_can_be_skipped(self) -> None:
        update_state.update_state(
            str(self.workspace), "doc", "skipped", note="approved small-fix exception"
        )
        with self.assertRaisesRegex(ValueError, "only the doc stage"):
            update_state.update_state(
                str(self.workspace), "rtl", "skipped", note="not allowed"
            )


if __name__ == "__main__":
    unittest.main()
