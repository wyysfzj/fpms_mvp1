from __future__ import annotations

import sys
import unittest
from datetime import datetime
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models import *  # noqa: E402,F401,F403  — configure the complete ORM registry
from app.modules.documents.evidence_contracts import (  # noqa: E402
    EvidenceReviewState,
    EvidenceRole,
)
from app.modules.documents.models import (  # noqa: E402
    DocAttachment,
    DocumentEvidenceVersion,
)
from app.modules.official_workflows.models import OfficialWorkPackage  # noqa: E402

CASE_ID = "00000000-0000-0000-0000-000000000001"
PACKAGE_ID = "00000000-0000-0000-0000-000000000002"
ATTACHMENT_ID = "00000000-0000-0000-0000-000000000003"
CREATOR_ID = "00000000-0000-0000-0000-000000000004"
REVIEWER_ID = "00000000-0000-0000-0000-000000000005"
REVIEWED_AT = datetime(2026, 7, 19, 16, 30)


def _version(**overrides: object) -> DocumentEvidenceVersion:
    values: dict[str, object] = {
        "id": "00000000-0000-0000-0000-000000000006",
        "case_id": CASE_ID,
        "document_id": "00000000-0000-0000-0000-000000000007",
        "attachment_id": ATTACHMENT_ID,
        "lineage_key": "filing-main",
        "role": EvidenceRole.FILING_FULL_WORD.value,
        "version_number": 1,
        "state": "DRAFT",
        "creator_id": CREATOR_ID,
        "review_state": EvidenceReviewState.APPROVED.value,
        "reviewer_id": REVIEWER_ID,
        "reviewed_at": REVIEWED_AT,
        "content_hash": f"sha256:{'a' * 64}",
        "current_identity_key": f"{CASE_ID}|filing-main",
    }
    values.update(overrides)
    return DocumentEvidenceVersion(**values)


class _ScalarRows:
    def __init__(self, rows: list[object]) -> None:
        self._rows = rows

    def scalars(self) -> _ScalarRows:
        return self

    def all(self) -> list[object]:
        return self._rows

    def first(self) -> object | None:
        return self._rows[0] if self._rows else None


class _ReadOnlySession:
    def __init__(self, *rows: list[object]) -> None:
        self._rows = list(rows)
        self.flush_count = 0

    def execute(self, _statement: object) -> _ScalarRows:
        return _ScalarRows(self._rows.pop(0))

    def flush(self) -> None:
        self.flush_count += 1


def _capture_manifest(
    calls: list[dict[str, object]],
    _db: object,
    **kwargs: object,
) -> object:
    calls.append(kwargs)
    return object()


class FilingFullWordReadinessPolicyTests(unittest.TestCase):
    def test_only_current_independently_approved_filing_full_word_is_ready(self) -> None:
        from app.modules.documents import evidence_policy

        self.assertTrue(
            evidence_policy.is_filing_full_word_ready(
                case_id=CASE_ID,
                evidence_version=_version(),
            )
        )

        rejected = (
            _version(role=EvidenceRole.RAW_ATTACHMENT.value),
            _version(review_state=EvidenceReviewState.PENDING.value),
            _version(reviewer_id=CREATOR_ID),
            _version(current_identity_key=None),
        )
        for evidence_version in rejected:
            with self.subTest(evidence_version=evidence_version):
                self.assertFalse(
                    evidence_policy.is_filing_full_word_ready(
                        case_id=CASE_ID,
                        evidence_version=evidence_version,
                    )
                )

    def test_refresh_projects_only_ready_full_word_to_the_manifest(self) -> None:
        from app.modules.official_workflows import service

        package = OfficialWorkPackage(
            id=PACKAGE_ID,
            case_id=CASE_ID,
            package_kind="FILING_PREP",
            status="PREPARING",
        )
        attachment = DocAttachment(
            id=ATTACHMENT_ID,
            document_id="00000000-0000-0000-0000-000000000007",
            file_name="filing.docx",
            file_path="attachments/filing.docx",
            official_file_role="FILING_FULL_WORD",
            content_hash=f"sha256:{'a' * 64}",
        )
        item = SimpleNamespace(
            attachment_id=ATTACHMENT_ID,
            official_file_role="FILING_FULL_WORD",
            external_upload_position="FILING_SOURCE_WORD",
        )
        summary = SimpleNamespace(
            intake_gate_roles=[],
            filing_roles=[item],
            archive_roles=[],
            historical_alias_roles=[],
        )
        result = object()

        for evidence_version, expected_attachment in (
            (_version(), attachment),
            (_version(reviewer_id=CREATOR_ID), None),
        ):
            with self.subTest(evidence_version=evidence_version):
                transaction = _ReadOnlySession([], [evidence_version])
                manifest_calls: list[dict[str, object]] = []

                with (
                    patch.object(service, "_case_attachments", return_value=[attachment]),
                    patch.object(
                        service,
                        "summarize_attachment_manifest",
                        return_value=summary,
                    ),
                    patch.object(
                        service,
                        "_upsert_manifest_role",
                        side_effect=partial(_capture_manifest, manifest_calls),
                    ),
                    patch.object(service, "_upsert_checklist"),
                    patch.object(
                        service,
                        "get_filing_preparation_package",
                        return_value=result,
                    ),
                ):
                    actual = service._refresh_filing_preparation_package(
                        transaction,  # type: ignore[arg-type]
                        package=package,
                    )

                self.assertIs(actual, result)
                full_word_call = next(
                    call for call in manifest_calls if call["role"] == "FILING_FULL_WORD"
                )
                self.assertIs(full_word_call["attachment"], expected_attachment)
                self.assertEqual(transaction.flush_count, 1)

    def test_evaluation_blocks_filing_package_when_full_word_manifest_is_absent(
        self,
    ) -> None:
        from app.modules.official_workflows import service

        package = OfficialWorkPackage(
            id=PACKAGE_ID,
            case_id=CASE_ID,
            package_kind="FILING_PREP",
            status="PREPARING",
        )
        transaction = _ReadOnlySession([], [], [])
        with (
            patch.object(
                service,
                "_get_package",
                return_value=package,
            ),
        ):
            result = service.evaluate_official_work_package(
                transaction,  # type: ignore[arg-type]
                package_id=PACKAGE_ID,
            )

        full_word_blocker = next(
            blocker for blocker in result.blockers if blocker.item_code == "FILING_FULL_WORD"
        )
        self.assertEqual(full_word_blocker.blocker_type, "MANIFEST_MISSING")
        self.assertEqual(full_word_blocker.status, "NEEDS_MAINTENANCE")
        self.assertFalse(result.can_archive)


if __name__ == "__main__":
    unittest.main()
