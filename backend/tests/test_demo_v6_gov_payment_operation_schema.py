from __future__ import annotations

import hashlib
import json
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.modules.billing.models import DemoFinanceCommand


def _command(operation: str) -> DemoFinanceCommand:
    actor_id = str(uuid4())
    snapshot = json.dumps(
        {"actor_id": actor_id, "operation": operation, "payload": {}},
        sort_keys=True,
        separators=(",", ":"),
    )
    return DemoFinanceCommand(
        id=str(uuid4()),
        operation=operation,
        idempotency_key=str(uuid4()),
        state="IN_PROGRESS",
        command_hash=hashlib.sha256(snapshot.encode("utf-8")).hexdigest(),
        command_snapshot=snapshot,
        created_by=actor_id,
        updated_by=actor_id,
    )


def test_demo_finance_operation_constraint_accepts_only_frozen_v6_operations(
    session_factory,
) -> None:
    with session_factory() as transaction:
        transaction.add(_command("GOV_PAYMENT"))
        transaction.commit()

    with session_factory() as transaction:
        transaction.add(_command("UNKNOWN"))
        with pytest.raises(IntegrityError):
            transaction.commit()
