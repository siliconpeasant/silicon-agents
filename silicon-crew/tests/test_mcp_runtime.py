from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from mcp_runtime import run_command


class McpRuntimeTest(unittest.TestCase):
    def test_nonzero_exit_is_error(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "exited with status 7"):
            run_command([sys.executable, "-c", "raise SystemExit(7)"])


if __name__ == "__main__":
    unittest.main()
