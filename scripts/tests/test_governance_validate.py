import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts/governance_validate.py"
TASK_ID = "REPO-GOVERNANCE-RESET-MODULES-20260716-01"
ARTIFACT_ROOT = REPO_ROOT / "artifacts" / TASK_ID

REQUIRED_FAMILIES = (
    "GOV-API-UI",
    "GOV-AUTH",
    "GOV-BEHAVIOR",
    "GOV-CUSTOMER",
    "GOV-DATA",
    "GOV-EVIDENCE",
    "GOV-FEE",
    "GOV-LEGACY",
    "GOV-LIFECYCLE",
    "GOV-LINEAGE",
    "GOV-LINT",
    "GOV-LIVENESS",
    "GOV-MULTIAGENT",
    "GOV-RELEASE",
    "GOV-REPORT",
    "GOV-RISK-RUNTIME",
    "GOV-RUNBOOK",
    "GOV-SCOPE",
    "GOV-SKILLS",
    "GOV-SOURCE",
    "GOV-SQLITE",
)

FAMILY_OWNERS = {
    "GOV-API-UI": ("GOV-API-UI-001", "docs/agents/domain-safety.md"),
    "GOV-AUTH": ("GOV-AUTH-001", "docs/agents/domain-safety.md"),
    "GOV-BEHAVIOR": ("GOV-BEHAVIOR-001", "AGENTS.md"),
    "GOV-CUSTOMER": ("GOV-CUSTOMER-001", "AGENTS.md"),
    "GOV-DATA": ("GOV-DATA-001", "docs/agents/domain-safety.md"),
    "GOV-EVIDENCE": ("GOV-EVIDENCE-001", "docs/agents/evidence.md"),
    "GOV-FEE": ("GOV-FEE-001", "docs/agents/domain-safety.md"),
    "GOV-LEGACY": ("GOV-LEGACY-001", "docs/agents/legacy-mvp1.md"),
    "GOV-LIFECYCLE": ("GOV-LIFECYCLE-001", "docs/agents/domain-safety.md"),
    "GOV-LINEAGE": ("GOV-LINEAGE-001", "docs/agents/domain-safety.md"),
    "GOV-LINT": ("GOV-LINT-001", "docs/agents/execution.md"),
    "GOV-LIVENESS": ("GOV-LIVENESS-001", "docs/agents/execution.md"),
    "GOV-MULTIAGENT": ("GOV-MULTIAGENT-001", "docs/agents/execution.md"),
    "GOV-RELEASE": ("GOV-RELEASE-001", "AGENTS.md"),
    "GOV-REPORT": ("GOV-REPORT-001", "docs/agents/execution.md"),
    "GOV-RISK-RUNTIME": ("GOV-RISK-RUNTIME-001", "docs/agents/execution.md"),
    "GOV-RUNBOOK": ("GOV-RUNBOOK-001", "docs/agents/execution.md"),
    "GOV-SCOPE": ("GOV-SCOPE-001", "docs/agents/execution.md"),
    "GOV-SKILLS": ("GOV-SKILLS-001", "AGENTS.md"),
    "GOV-SOURCE": ("GOV-SOURCE-001", "docs/agents/source-authority.md"),
    "GOV-SQLITE": ("GOV-SQLITE-001", "docs/agents/domain-safety.md"),
}


def _rule(rule_id: str) -> str:
    return f"### Rule {rule_id} — Contract\n\nThe rule remains authoritative.\n"


class CandidateFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.module_root = root / "docs/agents"
        self.candidate_root = root / "candidate"
        self.ledger_root = root / "analysis"
        self.module_root.mkdir(parents=True)
        self.candidate_root.mkdir(parents=True)
        self.ledger_root.mkdir(parents=True)

        self.current_root = root / "AGENTS.md"
        self.root_candidate = self.candidate_root / "AGENTS.md"
        self.manifest_candidate = self.candidate_root / "manifest.json"
        self.ledger_path = self.ledger_root / "current_rule_disposition.json"

        self.current_root.write_text(
            "# Current governance\n\n## Current scope\n\nCurrent rule.\n",
            encoding="utf-8",
        )
        self.root_candidate.write_text(self._root_text(), encoding="utf-8")
        self.modules = self._module_texts()
        for relative_path, content in self.modules.items():
            (root / relative_path).write_text(content, encoding="utf-8")
        self.manifest = self._manifest()
        self.write_manifest()
        self.ledger = self._ledger()
        self.write_ledger()

    def _root_text(self) -> str:
        declarations = "\n".join(
            _rule(FAMILY_OWNERS[family][0])
            for family in ("GOV-BEHAVIOR", "GOV-CUSTOMER", "GOV-RELEASE", "GOV-SKILLS")
        )
        refs = "\n".join(
            f"Rule-Ref: {FAMILY_OWNERS[family][0]}"
            for family in REQUIRED_FAMILIES
            if FAMILY_OWNERS[family][1] != "AGENTS.md"
        )
        return (
            "# Candidate governance\n\n"
            "[Modules](docs/agents/README.md)\n\n"
            "[Manifest](docs/agents/manifest.json)\n\n"
            f"{declarations}\n{refs}\n"
        )

    def _module_texts(self) -> dict[str, str]:
        grouped: dict[str, list[str]] = {
            "docs/agents/README.md": ["GOV-MODULES-001"],
            "docs/agents/domain-safety.md": [],
            "docs/agents/execution.md": [],
            "docs/agents/evidence.md": [],
            "docs/agents/source-authority.md": [],
            "docs/agents/legacy-mvp1.md": [],
        }
        for family in REQUIRED_FAMILIES:
            rule_id, owner = FAMILY_OWNERS[family]
            if owner != "AGENTS.md":
                grouped[owner].append(rule_id)
        return {
            path: f"# {Path(path).stem}\n\n" + "\n".join(_rule(item) for item in ids)
            for path, ids in grouped.items()
        }

    def _manifest(self) -> dict[str, object]:
        rule_owners = {"GOV-MODULES-001": "docs/agents/README.md"}
        rule_owners.update(
            {
                FAMILY_OWNERS[item][0]: FAMILY_OWNERS[item][1]
                for item in REQUIRED_FAMILIES
            }
        )
        return {
            "schema_version": 2,
            "active_version": "2.0.0",
            "adapter_version": "2.0.0",
            "activation_task": "REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01",
            "required_closure_tags": [
                "fee",
                "governance",
                "legacy",
                "source-authority",
            ],
            "rule_owners": rule_owners,
            "modules": [
                {"path": "docs/agents/README.md", "always": True, "selectors": []},
                {"path": "docs/agents/evidence.md", "always": True, "selectors": []},
                {"path": "docs/agents/execution.md", "always": True, "selectors": []},
                {
                    "path": "docs/agents/domain-safety.md",
                    "always": False,
                    "selectors": [
                        {"risk_any": ["HIGH"]},
                        {"closure_tag_any": ["fee"]},
                    ],
                },
                {
                    "path": "docs/agents/legacy-mvp1.md",
                    "always": False,
                    "selectors": [
                        {"closure_tag_any": ["legacy"]},
                        {"task_path_any": ["tasks/backend/**"]},
                    ],
                },
                {
                    "path": "docs/agents/source-authority.md",
                    "always": False,
                    "selectors": [
                        {"closure_tag_any": ["governance", "source-authority"]}
                    ],
                },
            ],
        }

    def _ledger(self) -> dict[str, object]:
        source = self.current_root.read_bytes()
        units = self._fixture_units()
        families = []
        for family in REQUIRED_FAMILIES:
            rule_id, owner = FAMILY_OWNERS[family]
            if owner == "AGENTS.md" or owner in {
                "docs/agents/evidence.md",
                "docs/agents/execution.md",
            }:
                selector = {"always": True}
            elif owner == "docs/agents/legacy-mvp1.md":
                selector = {"closure_tag_any": ["legacy"]}
            elif owner == "docs/agents/source-authority.md":
                selector = {"closure_tag_any": ["source-authority"]}
            elif family == "GOV-FEE":
                selector = {"closure_tag_any": ["fee"]}
            else:
                selector = {"risk_any": ["HIGH"]}
            families.append(
                {
                    "family": family,
                    "owner_rule": rule_id,
                    "owner_path": owner,
                    "selector": selector,
                    "activation_check": f"Validate {family} owner and references.",
                }
            )
        return {
            "schema_version": 1,
            "source": {
                "path": "AGENTS.md",
                "sha256": hashlib.sha256(source).hexdigest(),
                "line_count": len(source.decode("utf-8").splitlines()),
                "inventory_algorithm": "markdown-logical-units-v1",
                "logical_unit_count": len(units),
            },
            "families": families,
            "entries": [
                {
                    **units[0],
                    "family": "GOV-BEHAVIOR",
                    "disposition": "PRESERVE",
                    "owner_rule": "GOV-BEHAVIOR-001",
                    "selector": {"always": True},
                    "reason": "Keep the governing behavior.",
                    "observable_activation_check": "Candidate validation returns zero.",
                },
                {
                    **units[1],
                    "family": "GOV-SCOPE",
                    "disposition": "MOVE",
                    "owner_rule": "GOV-SCOPE-001",
                    "selector": {"always": True},
                    "reason": "Move execution detail to its sole owner.",
                    "observable_activation_check": "Candidate validation returns zero.",
                },
                {
                    **units[2],
                    "family": "GOV-SCOPE",
                    "disposition": "MOVE",
                    "owner_rule": "GOV-SCOPE-001",
                    "selector": {"always": True},
                    "reason": "Move execution detail to its sole owner.",
                    "observable_activation_check": "Candidate validation returns zero.",
                },
            ],
        }

    def _fixture_units(self) -> list[dict[str, object]]:
        units = []
        for line_number, text in enumerate(
            self.current_root.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not text:
                continue
            kind = "heading" if text.startswith("#") else "prose"
            units.append(
                {
                    "current_location": (
                        f"AGENTS.md:{line_number}-{line_number}:{kind}"
                    ),
                    "unit_kind": kind,
                    "start_line": line_number,
                    "end_line": line_number,
                    "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                }
            )
        return units

    def write_manifest(self) -> None:
        self.manifest_candidate.write_text(
            json.dumps(self.manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def write_ledger(self) -> None:
        self.ledger_path.write_text(
            json.dumps(self.ledger, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def refresh_source_identity(self) -> None:
        source = self.current_root.read_bytes()
        self.ledger["source"]["sha256"] = hashlib.sha256(source).hexdigest()
        self.ledger["source"]["line_count"] = len(source.decode("utf-8").splitlines())
        self.ledger["source"]["logical_unit_count"] = len(self._fixture_units())
        self.write_ledger()


class GovernanceValidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

    def fixture(self, name: str = "fixture") -> CandidateFixture:
        return CandidateFixture(self.root / name)

    def run_fixture(
        self, fixture: CandidateFixture
    ) -> subprocess.CompletedProcess[str]:
        self.assertTrue(
            VALIDATOR.is_file(), "missing governance validator implementation"
        )
        return subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                "--root-candidate",
                str(fixture.root_candidate),
                "--manifest-candidate",
                str(fixture.manifest_candidate),
                "--disposition-ledger",
                str(fixture.ledger_path),
            ],
            cwd=fixture.root,
            check=False,
            capture_output=True,
            text=True,
        )

    def assert_invalid(self, fixture: CandidateFixture, expected: str) -> None:
        result = self.run_fixture(fixture)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected, result.stderr)

    def load_validator(self):
        self.assertTrue(
            VALIDATOR.is_file(), "missing governance validator implementation"
        )
        spec = importlib.util.spec_from_file_location("governance_validate", VALIDATOR)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_valid_candidate_and_repository_candidate_pass(self) -> None:
        fixture = self.fixture()
        result = self.run_fixture(fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        digest = fixture.candidate_root / "governance_digest.json"
        self.assertTrue(digest.is_file())
        self.assertRegex(json.loads(digest.read_text())["digest"], r"^[0-9a-f]{64}$")

        repository_result = subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                "--root-candidate",
                str(ARTIFACT_ROOT / "candidate/AGENTS.md"),
                "--manifest-candidate",
                str(ARTIFACT_ROOT / "candidate/manifest.json"),
                "--disposition-ledger",
                str(ARTIFACT_ROOT / "analysis/current_rule_disposition.json"),
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(repository_result.returncode, 0, repository_result.stderr)

    def test_rejects_invalid_rule_declaration_reference_and_owner(self) -> None:
        cases = (
            "duplicate",
            "missing-reference",
            "self-reference",
            "wrong-owner",
            "bad-id",
        )
        for case in cases:
            with self.subTest(case=case):
                fixture = self.fixture(case)
                if case == "duplicate":
                    path = fixture.root / "docs/agents/execution.md"
                    path.write_text(path.read_text() + _rule("GOV-FEE-001"))
                    expected = "declared more than once"
                elif case == "missing-reference":
                    fixture.root_candidate.write_text(
                        fixture.root_candidate.read_text()
                        + "Rule-Ref: GOV-MISSING-001\n"
                    )
                    expected = "undefined Rule-Ref"
                elif case == "self-reference":
                    path = fixture.root / "docs/agents/domain-safety.md"
                    path.write_text(path.read_text() + "Rule-Ref: GOV-FEE-001\n")
                    expected = "references its own rule"
                elif case == "wrong-owner":
                    fixture.manifest["rule_owners"]["GOV-FEE-001"] = (
                        "docs/agents/execution.md"
                    )
                    fixture.write_manifest()
                    expected = "owner mismatch"
                else:
                    path = fixture.root / "docs/agents/execution.md"
                    path.write_text(path.read_text() + "### Rule bad-id — Invalid\n")
                    expected = "invalid Rule declaration"
                self.assert_invalid(fixture, expected)

    def test_rejects_invalid_selector_shapes_and_paths(self) -> None:
        cases = (
            "parent-path",
            "backslash",
            "unsupported-glob",
            "always-selectors",
            "conditional-empty",
            "unknown-field",
            "missing-tag-route",
            "symlink",
        )
        for case in cases:
            with self.subTest(case=case):
                fixture = self.fixture(case)
                module = fixture.manifest["modules"][3]
                expected = "selector"
                if case == "parent-path":
                    module["path"] = "docs/agents/../escape.md"
                    expected = "unsafe module path"
                elif case == "backslash":
                    module["path"] = "docs\\agents\\domain-safety.md"
                    expected = "unsafe module path"
                elif case == "unsupported-glob":
                    module["selectors"] = [{"task_path_any": ["tasks/?ad/**"]}]
                    expected = "unsupported glob"
                elif case == "always-selectors":
                    module["always"] = True
                    expected = "always module must have empty selectors"
                elif case == "conditional-empty":
                    module["selectors"] = []
                    expected = "conditional module requires selectors"
                elif case == "unknown-field":
                    module["selectors"] = [{"risk_all": ["HIGH"]}]
                    expected = "unknown selector field"
                elif case == "missing-tag-route":
                    fixture.manifest["required_closure_tags"].append("lineage")
                    fixture.manifest["required_closure_tags"].sort()
                    expected = "required closure tag has no module"
                else:
                    target = fixture.root / "outside.md"
                    target.write_text("# outside\n")
                    link = fixture.root / "docs/agents/symlink.md"
                    link.symlink_to(target)
                    module["path"] = "docs/agents/symlink.md"
                    expected = "symlink module path"
                fixture.write_manifest()
                self.assert_invalid(fixture, expected)

    def test_rejects_invalid_link_fence_line_limit_module_and_version(self) -> None:
        cases = ("link", "fence", "line-limit", "undeclared-module", "version")
        for case in cases:
            with self.subTest(case=case):
                fixture = self.fixture(case)
                if case == "link":
                    fixture.root_candidate.write_text(
                        fixture.root_candidate.read_text()
                        + "[Missing](docs/agents/missing.md)\n"
                    )
                    expected = "broken internal link"
                elif case == "fence":
                    fixture.root_candidate.write_text(
                        fixture.root_candidate.read_text() + "```\n"
                    )
                    expected = "unclosed Markdown fence"
                elif case == "line-limit":
                    fixture.root_candidate.write_text(
                        fixture.root_candidate.read_text() + "padding\n" * 301
                    )
                    expected = "exceeds 300 lines"
                elif case == "undeclared-module":
                    (fixture.root / "docs/agents/extra.md").write_text("# Extra\n")
                    expected = "undeclared normative module"
                else:
                    fixture.manifest["adapter_version"] = "1.1.0"
                    fixture.write_manifest()
                    expected = "version mismatch"
                self.assert_invalid(fixture, expected)

    def test_rejects_each_omitted_preservation_family(self) -> None:
        for family in REQUIRED_FAMILIES:
            with self.subTest(family=family):
                fixture = self.fixture(family.lower())
                fixture.ledger["families"] = [
                    item
                    for item in fixture.ledger["families"]
                    if item["family"] != family
                ]
                fixture.write_ledger()
                self.assert_invalid(fixture, f"missing preservation family: {family}")

    def test_rejects_incomplete_disposition_coverage_and_unsafe_removal(self) -> None:
        cases = ("coverage", "activation", "removal", "unknown-owner")
        for case in cases:
            with self.subTest(case=case):
                fixture = self.fixture(case)
                if case == "coverage":
                    fixture.ledger["entries"].pop()
                    expected = "missing current logical unit disposition"
                elif case == "activation":
                    fixture.ledger["entries"][0]["observable_activation_check"] = ""
                    expected = "missing observable activation check"
                elif case == "removal":
                    fixture.ledger["entries"][0]["disposition"] = "REMOVE"
                    expected = "REMOVE requires design approval"
                else:
                    fixture.ledger["entries"][0]["owner_rule"] = "GOV-NOT-DECLARED-001"
                    expected = "ledger owner rule is not declared"
                fixture.write_ledger()
                self.assert_invalid(fixture, expected)

    def test_rejects_unaccounted_or_changed_authoritative_logical_unit(self) -> None:
        for case in ("append", "change"):
            with self.subTest(case=case):
                fixture = self.fixture(f"logical-unit-{case}")
                current = fixture.current_root.read_text(encoding="utf-8")
                if case == "append":
                    current += "\nNew authoritative requirement.\n"
                else:
                    current = current.replace(
                        "Current rule.", "Changed authoritative rule."
                    )
                fixture.current_root.write_text(current, encoding="utf-8")
                fixture.refresh_source_identity()
                self.assert_invalid(fixture, "logical unit")

    def test_rejects_invalid_family_and_entry_ledger_selectors(self) -> None:
        mutations = {
            "unknown-field": {"risk_all": ["HIGH"]},
            "unsafe-path": {"task_path_any": ["tasks/../**"]},
            "unsafe-glob": {"task_path_any": ["tasks/?ad/**"]},
            "invalid-value": {"closure_tag_any": ["Fee"]},
            "always-mix": {"always": True, "risk_any": ["HIGH"]},
            "non-routing-owner": {"closure_tag_any": ["source-authority"]},
        }
        for target in ("family", "entry"):
            for case, selector in mutations.items():
                with self.subTest(target=target, case=case):
                    fixture = self.fixture(f"ledger-selector-{target}-{case}")
                    if target == "family":
                        item = next(
                            family
                            for family in fixture.ledger["families"]
                            if family["family"] == "GOV-FEE"
                        )
                    else:
                        item = fixture.ledger["entries"][1]
                        item["family"] = "GOV-FEE"
                        item["owner_rule"] = "GOV-FEE-001"
                    item["selector"] = selector
                    fixture.write_ledger()
                    self.assert_invalid(fixture, "ledger selector")

    def test_rejects_non_boolean_always_for_family_and_entry(self) -> None:
        for target in ("family", "entry"):
            with self.subTest(target=target):
                fixture = self.fixture(f"ledger-always-type-{target}")
                if target == "family":
                    item = next(
                        family
                        for family in fixture.ledger["families"]
                        if family["family"] == "GOV-SCOPE"
                    )
                else:
                    item = fixture.ledger["entries"][1]
                item["selector"] = {"always": 1}
                fixture.write_ledger()
                self.assert_invalid(fixture, "ledger selector")

    def test_repository_modules_preserve_reviewed_omissions(self) -> None:
        execution = (REPO_ROOT / "docs/agents/execution.md").read_text(encoding="utf-8")
        source_authority = (REPO_ROOT / "docs/agents/source-authority.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("remaining follow-up task IDs, or `None`", execution)
        self.assertIn("one exact closure slice, not one module cluster", execution)
        self.assertIn("`close the remaining module`", execution)
        self.assertIn("`finish the whole chain`", execution)
        self.assertIn("`complete backend/frontend parity`", execution)
        self.assertIn("`close the remaining feasible scope`", execution)
        self.assertIn(
            "FPMS_Automation_Skeleton_Pack/docs/source/FPMS_SPEC_2_0.md",
            source_authority,
        )

    def test_task_metadata_and_selector_matching_are_fail_closed(self) -> None:
        validator = self.load_validator()
        valid = (
            "# Task\n\n"
            "Status: READY\n"
            "Risk-Tier: HIGH\n"
            'Closure-Tags: ["fee", "governance"]\n'
            "Task-Path: tasks/postdemo/example.md\n\n"
            "## Contract\n"
        )
        metadata = validator.parse_task_metadata(valid, "tasks/postdemo/example.md")
        self.assertEqual(metadata["risk_tier"], "HIGH")

        invalid_metadata = (
            valid.replace("Risk-Tier: HIGH", "Risk-Tier: `HIGH`"),
            valid.replace(
                'Closure-Tags: ["fee", "governance"]',
                'Closure-Tags: ["governance", "fee"]',
            ),
            valid.replace(
                "Task-Path: tasks/postdemo/example.md", "Task-Path: other.md"
            ),
            valid.replace("Risk-Tier: HIGH\n", ""),
            valid.replace("Task-Path:", "Task-Path: duplicate.md\nTask-Path:"),
        )
        for text in invalid_metadata:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    validator.parse_task_metadata(text, "tasks/postdemo/example.md")

        fixture = self.fixture("selection")
        selected, trace = validator.select_modules(
            fixture.manifest,
            {
                "risk_tier": "HIGH",
                "closure_tags": ["governance"],
                "task_path": "tasks/postdemo/example.md",
            },
        )
        self.assertEqual(selected, sorted(selected))
        self.assertIn("docs/agents/domain-safety.md", selected)
        self.assertIn("docs/agents/source-authority.md", selected)
        self.assertTrue(trace)


if __name__ == "__main__":
    unittest.main()
