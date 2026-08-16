from __future__ import annotations

import json
import os
import re
from pathlib import Path

from app.core.demo_bundle import (
    DemoBundleError,
    demo_bundle_forbidden_roots,
    load_demo_bundle,
)

_RUN_ID_RE = re.compile(r"[A-Za-z0-9._-]{1,96}")


def _required_env(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise DemoBundleError(f"DEMO_INPUT_INVALID: required environment variable {name} is missing")
    return value


def main() -> int:
    if _required_env("FPMS_ENV") != "demo":
        raise DemoBundleError("DEMO_INPUT_INVALID: FPMS_ENV must be demo")
    if _required_env("FPMS_DEMO_SCOPE") != "LOCAL_ABC_E2E":
        raise DemoBundleError("DEMO_INPUT_INVALID: FPMS_DEMO_SCOPE must be LOCAL_ABC_E2E")
    run_profile = _required_env("FPMS_DEMO_RUN_PROFILE")
    run_id = _required_env("FPMS_DEMO_RUN_ID")
    if _RUN_ID_RE.fullmatch(run_id) is None:
        raise DemoBundleError("DEMO_INPUT_INVALID: FPMS_DEMO_RUN_ID has invalid format")

    bundle_path = Path(_required_env("FPMS_DEMO_BUNDLE_PATH"))
    forbidden_roots = demo_bundle_forbidden_roots(
        bundle_path,
        run_id=run_id,
        configured_storage=os.environ.get("STORAGE_DIR"),
    )
    snapshot = load_demo_bundle(
        bundle_path,
        expected_manifest_sha256=_required_env("FPMS_DEMO_EXPECTED_MANIFEST_SHA256"),
        expected_authority_sha256=_required_env("FPMS_DEMO_EXPECTED_AUTHORITY_SHA256"),
        expected_authority_classification=_required_env(
            "FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION"
        ),
        repo_root=Path(__file__).resolve().parents[2],
        forbidden_roots=forbidden_roots,
    )
    required_profile = (
        "TECHNICAL_REHEARSAL"
        if snapshot.authority_classification == "SYNTHETIC_TEST_ONLY"
        else "CUSTOMER_DEMO"
    )
    if run_profile != required_profile:
        raise DemoBundleError(
            "DEMO_INPUT_INVALID: authority classification and run profile do not match"
        )
    print(
        json.dumps(
            {
                "status": "VALID",
                "run_id": run_id,
                "run_profile": run_profile,
                "bundle_id": snapshot.bundle_id,
                "bundle_version": snapshot.bundle_version,
                "manifest_sha256": snapshot.manifest_sha256,
                "authority_sha256": snapshot.authority_sha256,
                "authority_classification": snapshot.authority_classification,
                "customer_activation_eligible": snapshot.customer_activation_eligible,
                "approved_by": snapshot.approved_by,
                "approved_at": snapshot.approved_at,
                "evaluated_date": snapshot.local_date.isoformat(),
                "timezone": "Asia/Shanghai",
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
