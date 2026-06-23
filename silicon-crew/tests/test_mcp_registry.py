from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class McpRegistryTest(unittest.TestCase):
    def test_expected_tools_are_registered(self) -> None:
        servers = {
            "soc-build": {
                "soc_init", "soc_add_ip", "soc_add_chip", "soc_flist", "soc_lint",
                "soc_comp", "soc_sim", "soc_regress", "soc_coverage", "soc_syn",
            },
            "soc-integrate": {
                "soc_extract", "soc_instantiate", "soc_integrate", "soc_wrap",
                "soc_csv", "soc_snapshot", "soc_diff", "soc_extract_map",
                "soc_update", "soc_remove",
            },
            "yml2reg": {"yml2reg"},
            "excel-yml-gen": {"excel_yml_gen"},
            "crg-req-to-design": {"crg_req_to_design"},
            "cr-tree-diag-gen": {
                "cr_tree_diag_gen", "cr_tree_diag_gen_drawio",
                "cr_tree_diag_gen_excalidraw",
            },
        }
        for name, expected in servers.items():
            path = ROOT / "skills" / name / "mcp_server.py"
            spec = importlib.util.spec_from_file_location(f"test_mcp_{name.replace('-', '_')}", path)
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
            registered = set(module.mcp._tool_manager._tools)
            self.assertEqual(expected, registered, name)


if __name__ == "__main__":
    unittest.main()
