from __future__ import annotations

import fcntl
import os
import stat
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.core.config import get_settings
from app.core.errors import raise_business_error
from app.core.storage import ensure_dir
from app.db.session import get_db
from app.modules.annuity.models import PayList
from app.modules.annuity.official_payment_workbook_input_schemas import (
    ActivateWorkbookInputIn,
    RetireWorkbookInputIn,
    ReviewWorkbookInputIn,
    WorkbookInputOut,
)
from app.modules.annuity.official_payment_workbook_input_service import (
    ActivateWorkbookInputCommand,
    RegisterWorkbookInputCommand,
    RetireWorkbookInputCommand,
    ReviewWorkbookInputCommand,
    ValidateWorkbookInputCommand,
    activate_workbook_input,
    register_workbook_input,
    retire_workbook_input,
    review_workbook_input,
    validate_workbook_input,
)
from app.modules.annuity.schemas import (
    AnnuityTaskListResponse,
    OfficialWorkbookAcceptanceIn,
    OfficialWorkbookAcceptanceOut,
)
from app.modules.annuity.service import (
    ExportInternalPayListCommand,
    GenerateOfficialPaymentWorkbookCommand,
    RecordOfficialWorkbookAcceptanceCommand,
    add_manual_gov_payment,
    compensate_internal_pay_list_export,
    compensate_official_payment_workbook,
    create_historical_pay_list,
    create_pay_list_from_fee_items,
    export_internal_pay_list,
    generate_fee_drafts_from_annuity_tasks,
    generate_official_payment_workbook,
    get_pay_list_detail,
    list_annuity_tasks_report,
    list_pay_lists,
    mark_pay_list_paid,
    record_official_workbook_acceptance,
    register_gov_payment,
    update_annuity_task_instruction,
)
from app.modules.annuity.verified_official_payment_workbook import OfficialPaymentRow
from app.modules.auth.models import T_User
from app.modules.cases.models import Case

router = APIRouter()

_PAYMENT_WORKBOOK_UPLOAD_LIMIT = 25 * 1024 * 1024

_ANNUITY_TRIGGER_RULE = "年费节点到期"
_ANNUITY_DEADLINE_RULE = (
    "以年费任务到期日为准；滞纳金按每超过规定缴费时间 1 个月加收当年全额年费 5% 提示"
)
_ANNUITY_FEE_NODE_EXPLANATION = (
    "年费费用节点：客户指示缴费后生成官费草单，进入官费清单并登记官方缴费回执。"
)


def _official_workbook_utcnow() -> datetime:
    return datetime.utcnow()


def _official_workbook_runtime_profile() -> str:
    return get_settings().fpms_env


class AnnuityInstructionUpdateIn(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=24)
    instruction_date: date | None = None


class AnnuityGenerateDraftsIn(BaseModel):
    task_ids: list[int] = Field(..., min_length=1)
    pay_next_year: bool = False
    currency: str = Field(default="CNY", min_length=1, max_length=8)


class AnnuityTaskGenerateIn(BaseModel):
    case_id: str = Field(..., min_length=1)


class PayListFromFeeItemsIn(BaseModel):
    fee_item_ids: list[str] = Field(..., min_length=1)
    planned_pay_date: date | None = None
    remark: str | None = None


class OfficialPaymentWorkbookRowIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    sequence_number: int = Field(..., ge=1)
    application_number: str = Field(..., min_length=1, max_length=128)
    business_type: str = Field(..., min_length=1, max_length=64)
    invoice_title: str = Field(..., min_length=1, max_length=256)
    unified_social_credit_code: str = Field(..., min_length=1, max_length=64)
    fee_type: str = Field(..., min_length=1, max_length=128)
    foreign_currency_amount: int | float | None = Field(
        default=None,
        ge=0,
        allow_inf_nan=False,
    )
    amount_cny: int | float = Field(..., ge=0, allow_inf_nan=False)
    remark: str | None = Field(default=None, max_length=512)

    @field_validator(
        "application_number",
        "business_type",
        "invoice_title",
        "unified_social_credit_code",
        "fee_type",
        "remark",
    )
    @classmethod
    def reject_spreadsheet_control_characters(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            value.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError("text must be valid UTF-8") from exc
        if any(ord(character) < 32 for character in value):
            raise ValueError("text must not contain control characters")
        return value


class OfficialPaymentWorkbookGenerateIn(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    idempotency_key: str = Field(..., min_length=1, max_length=128)
    rows: list[OfficialPaymentWorkbookRowIn] = Field(..., min_length=1, max_length=500)


class HistoricalPayListCreateIn(BaseModel):
    client_id: str | None = Field(default=None, max_length=36)
    currency: str = Field(default="CNY", min_length=1, max_length=8)
    planned_pay_date: date | None = None
    remark: str | None = None
    list_type: str | None = Field(default=None, max_length=32)
    flow_dir: str | None = Field(default=None, max_length=32)
    invoice_no_from: str | None = Field(default=None, max_length=64)
    invoice_no_to: str | None = Field(default=None, max_length=64)


class GovPaymentCreateIn(BaseModel):
    pay_list_id: int
    fee_item_id: str = Field(..., min_length=1, max_length=36)
    paid_date: date | None = None
    paid_amount: Decimal | None = None
    official_receipt_no: str | None = Field(default=None, max_length=64)
    remark: str | None = None
    paid_currency: str | None = Field(default=None, max_length=8)
    voucher_no: str | None = Field(default=None, max_length=64)
    invoice_no: str | None = Field(default=None, max_length=64)


class ManualGovPaymentCreateIn(BaseModel):
    case_id: str = Field(..., min_length=1, max_length=36)
    fee_item_id: str | None = Field(default=None, max_length=36)
    paid_date: date
    paid_amount: Decimal = Field(..., gt=0)
    official_receipt_no: str | None = Field(default=None, max_length=64)
    remark: str | None = None
    fee_code: str | None = Field(default=None, max_length=64)
    year_no: int | None = Field(default=None, ge=1)
    paid_currency: str | None = Field(default=None, max_length=8)
    voucher_no: str | None = Field(default=None, max_length=64)
    invoice_no: str | None = Field(default=None, max_length=64)


class PayListMarkPaidIn(BaseModel):
    paid_date: date


def _utcnow() -> datetime:
    return datetime.utcnow()


def _runtime_profile() -> str:
    return get_settings().fpms_env


def _payment_workbook_storage_root() -> Path:
    return Path(get_settings().storage_dir).resolve() / "payment-workbook-inputs"


@contextmanager
def _payment_workbook_registration_lock(root: Path):
    ensure_dir(str(root.parent))
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(root.parent, flags)
    except OSError:
        raise_business_error(
            "PAYMENT_WORKBOOK_INPUT_CONFLICT",
            "Official payment workbook storage is unavailable",
            status_code=409,
        )
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
    except OSError:
        os.close(descriptor)
        raise_business_error(
            "PAYMENT_WORKBOOK_INPUT_CONFLICT",
            "Official payment workbook storage lock is unavailable",
            status_code=409,
        )
    try:
        yield
    finally:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def _upload_hash(upload: UploadFile, field: str) -> str:
    digest = sha256()
    size = 0
    try:
        upload.file.seek(0)
        while chunk := upload.file.read(1024 * 1024):
            size += len(chunk)
            if size > _PAYMENT_WORKBOOK_UPLOAD_LIMIT:
                raise_business_error(
                    "PAYMENT_WORKBOOK_INPUT_INVALID",
                    "Official payment workbook input is too large",
                    details={"field": field},
                    status_code=400,
                )
            digest.update(chunk)
        upload.file.seek(0)
    except OSError:
        raise_business_error(
            "PAYMENT_WORKBOOK_INPUT_INVALID",
            "Official payment workbook input cannot be read",
            details={"field": field},
            status_code=400,
        )
    return digest.hexdigest()


def _managed_file_hash(path: Path) -> str:
    digest = sha256()
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(descriptor, "rb") as stream:
            stat_result = os.fstat(stream.fileno())
            if (
                not stat.S_ISREG(stat_result.st_mode)
                or stat_result.st_size > _PAYMENT_WORKBOOK_UPLOAD_LIMIT
            ):
                raise OSError("invalid managed file")
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    except OSError:
        raise_business_error(
            "PAYMENT_WORKBOOK_INPUT_CONFLICT",
            "Official payment workbook managed file conflict",
            status_code=409,
        )
    return digest.hexdigest()


def _save_upload_no_follow(
    upload: UploadFile,
    directory: Path,
    name: str,
    identity: tuple[int, int],
) -> None:
    directory_descriptor: int | None = None
    file_descriptor: int | None = None
    try:
        directory_descriptor = os.open(
            directory,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        opened_directory = os.fstat(directory_descriptor)
        if (opened_directory.st_dev, opened_directory.st_ino) != identity:
            raise OSError("managed directory changed")
        file_descriptor = os.open(
            name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=directory_descriptor,
        )
        with os.fdopen(file_descriptor, "wb") as target:
            file_descriptor = None
            upload.file.seek(0)
            while chunk := upload.file.read(1024 * 1024):
                target.write(chunk)
            upload.file.seek(0)
    except OSError:
        raise_business_error(
            "PAYMENT_WORKBOOK_INPUT_CONFLICT",
            "Official payment workbook managed file conflict",
            status_code=409,
        )
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        if directory_descriptor is not None:
            os.close(directory_descriptor)


def _directory_identity(directory: Path) -> tuple[int, int]:
    try:
        current = directory.lstat()
    except OSError:
        raise_business_error(
            "PAYMENT_WORKBOOK_INPUT_CONFLICT",
            "Official payment workbook managed directory conflict",
            status_code=409,
        )
    if not stat.S_ISDIR(current.st_mode) or stat.S_ISLNK(current.st_mode):
        raise_business_error(
            "PAYMENT_WORKBOOK_INPUT_CONFLICT",
            "Official payment workbook managed directory conflict",
            status_code=409,
        )
    return current.st_dev, current.st_ino


def _remove_created_workbook_files(
    root: Path,
    directory: Path,
    identity: tuple[int, int],
) -> None:
    descriptor: int | None = None
    try:
        descriptor = os.open(
            directory,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != identity:
            return
        for name in ("template.xlsm", "upload-proof.bin"):
            try:
                os.unlink(name, dir_fd=descriptor)
            except FileNotFoundError:
                pass
    except OSError:
        return
    finally:
        if descriptor is not None:
            os.close(descriptor)
    try:
        if _directory_identity(directory) != identity:
            return
        directory.rmdir()
        root.rmdir()
    except Exception:
        pass


def _store_workbook_uploads(
    template_file: UploadFile,
    upload_proof_file: UploadFile,
    idempotency_key: str,
) -> tuple[Path, Path, str, str, tuple[int, int] | None]:
    if Path(template_file.filename or "").suffix.lower() != ".xlsm":
        raise_business_error(
            "PAYMENT_WORKBOOK_INPUT_INVALID",
            "Official payment workbook must be an .xlsm file",
            details={"field": "template_file"},
            status_code=400,
        )
    template_hash = _upload_hash(template_file, "template_file")
    proof_hash = _upload_hash(upload_proof_file, "upload_proof_file")
    root = _payment_workbook_storage_root()
    ensure_dir(str(root))
    directory = root / sha256(idempotency_key.encode()).hexdigest()
    template_path = directory / "template.xlsm"
    proof_path = directory / "upload-proof.bin"
    created_identity: tuple[int, int] | None = None
    try:
        directory.mkdir(exist_ok=False)
        created_identity = _directory_identity(directory)
        _save_upload_no_follow(
            template_file,
            directory,
            template_path.name,
            created_identity,
        )
        if _directory_identity(directory) != created_identity:
            raise OSError("managed directory changed")
        _save_upload_no_follow(
            upload_proof_file,
            directory,
            proof_path.name,
            created_identity,
        )
        if _directory_identity(directory) != created_identity:
            raise OSError("managed directory changed")
    except FileExistsError:
        try:
            directory_mode = directory.lstat().st_mode
        except OSError:
            directory_mode = 0
        if not stat.S_ISDIR(directory_mode) or stat.S_ISLNK(directory_mode):
            raise_business_error(
                "PAYMENT_WORKBOOK_INPUT_CONFLICT",
                "Official payment workbook managed directory conflict",
                status_code=409,
            )
    except Exception:
        if created_identity is not None:
            _remove_created_workbook_files(root, directory, created_identity)
        raise
    if (
        _managed_file_hash(template_path) != template_hash
        or _managed_file_hash(proof_path) != proof_hash
    ):
        if created_identity is not None:
            _remove_created_workbook_files(root, directory, created_identity)
        raise_business_error(
            "PAYMENT_WORKBOOK_INPUT_CONFLICT",
            "Official payment workbook replay content conflict",
            status_code=409,
        )
    return template_path, proof_path, template_hash, proof_hash, created_identity


@router.post(
    "/payment-workbook-inputs",
    response_model=WorkbookInputOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register official payment workbook input",
)
def post_payment_workbook_input(
    response: Response,
    template_file: UploadFile = File(...),
    upload_proof_file: UploadFile = File(...),
    template_version: str = Form(..., min_length=1, max_length=128),
    effective_from: datetime = Form(...),
    effective_to: datetime | None = Form(default=None),
    source_classification: str = Form(..., min_length=1, max_length=16),
    idempotency_key: str = Form(..., min_length=1, max_length=128),
    _perm: None = Depends(require_perm("Fee.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> WorkbookInputOut:
    root = _payment_workbook_storage_root()
    directory: Path | None = None
    created_identity: tuple[int, int] | None = None
    with _payment_workbook_registration_lock(root):
        try:
            template_path, proof_path, template_hash, proof_hash, created_identity = (
                _store_workbook_uploads(
                    template_file,
                    upload_proof_file,
                    idempotency_key,
                )
            )
            directory = template_path.parent
            result = register_workbook_input(
                db,
                RegisterWorkbookInputCommand(
                    template_version=template_version,
                    template_storage_path=str(template_path),
                    expected_template_hash=template_hash,
                    upload_proof_storage_path=str(proof_path),
                    expected_upload_proof_hash=proof_hash,
                    effective_from=effective_from,
                    effective_to=effective_to,
                    source_classification=source_classification,
                    actor_id=str(current_user.id),
                    idempotency_key=idempotency_key,
                    runtime_profile=_runtime_profile(),
                ),
            )
            db.commit()
        except Exception:
            db.rollback()
            if created_identity is not None and directory is not None:
                _remove_created_workbook_files(root, directory, created_identity)
            raise
    response.status_code = (
        status.HTTP_201_CREATED if result.disposition == "CREATED" else status.HTTP_200_OK
    )
    return WorkbookInputOut.model_validate(result)


@router.post(
    "/payment-workbook-inputs/{version_id}/validate",
    response_model=WorkbookInputOut,
    summary="Validate official payment workbook input",
)
def post_payment_workbook_input_validate(
    version_id: str,
    _perm: None = Depends(require_perm("Fee.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> WorkbookInputOut:
    try:
        result = validate_workbook_input(
            db,
            ValidateWorkbookInputCommand(
                version_id=version_id,
                actor_id=str(current_user.id),
            ),
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return WorkbookInputOut.model_validate(result)


@router.post(
    "/payment-workbook-inputs/{version_id}/review",
    response_model=WorkbookInputOut,
    summary="Review official payment workbook input",
)
def post_payment_workbook_input_review(
    version_id: str,
    payload: ReviewWorkbookInputIn,
    _perm: None = Depends(require_perm("Fee.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> WorkbookInputOut:
    try:
        result = review_workbook_input(
            db,
            ReviewWorkbookInputCommand(
                version_id=version_id,
                decision=payload.decision,
                reason=payload.reason,
                actor_id=str(current_user.id),
            ),
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return WorkbookInputOut.model_validate(result)


@router.post(
    "/payment-workbook-inputs/{version_id}/activate",
    response_model=WorkbookInputOut,
    summary="Activate official payment workbook input",
)
def post_payment_workbook_input_activate(
    version_id: str,
    payload: ActivateWorkbookInputIn,
    _perm: None = Depends(require_perm("Fee.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> WorkbookInputOut:
    try:
        result = activate_workbook_input(
            db,
            ActivateWorkbookInputCommand(
                version_id=version_id,
                actor_id=str(current_user.id),
                at=_utcnow(),
                idempotency_key=payload.idempotency_key,
                runtime_profile=_runtime_profile(),
            ),
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return WorkbookInputOut.model_validate(result)


@router.post(
    "/payment-workbook-inputs/{version_id}/retire",
    response_model=WorkbookInputOut,
    summary="Retire official payment workbook input",
)
def post_payment_workbook_input_retire(
    version_id: str,
    payload: RetireWorkbookInputIn,
    _perm: None = Depends(require_perm("Fee.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> WorkbookInputOut:
    try:
        result = retire_workbook_input(
            db,
            RetireWorkbookInputCommand(
                version_id=version_id,
                reason=payload.reason,
                actor_id=str(current_user.id),
                at=_utcnow(),
                idempotency_key=payload.idempotency_key,
            ),
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return WorkbookInputOut.model_validate(result)


def _annuity_deadline_preview_fields(year_no: int) -> dict[str, str]:
    return {
        "trigger_rule": _ANNUITY_TRIGGER_RULE,
        "deadline_rule": _ANNUITY_DEADLINE_RULE,
        "fee_basis": f"第{year_no}年度年费，按专利类型和年度阶梯费率预估",
        "fee_node_explanation": _ANNUITY_FEE_NODE_EXPLANATION,
    }


@router.get("/annuity/tasks", response_model=AnnuityTaskListResponse, summary="List annuity tasks")
def get_annuity_tasks(
    due_from: date | None = Query(default=None),
    due_to: date | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    status: str | None = Query(default=None),
    task_status: str | None = Query(default=None),
    pending_mode: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    country: str | None = Query(default=None),
    annuity_year: int | None = Query(default=None, ge=1),
    payment_status: str | None = Query(default=None),
    notice_status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("AnnuityTask.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List annuity tasks with filters and pagination."""
    filters = {
        "due_from": due_from,
        "due_to": due_to,
        "date_from": date_from,
        "date_to": date_to,
        "status": status,
        "task_status": task_status,
        "pending_mode": pending_mode,
        "case_id": case_id,
        "case_no": case_no,
        "client_id": client_id,
        "country": country,
        "annuity_year": annuity_year,
        "payment_status": payment_status,
        "notice_status": notice_status,
    }
    tasks, total, summary = list_annuity_tasks_report(
        db, filters=filters, page=page, page_size=page_size
    )
    case_no_map: dict[str, str] = {}
    case_ids = sorted({task.case_id for task in tasks})
    if case_ids:
        cases = db.query(Case.id, Case.case_no).filter(Case.id.in_(case_ids)).all()
        case_no_map = {case.id: case.case_no for case in cases}

    items = [
        {
            "id": task.id,
            "case_id": task.case_id,
            "case_no": case_no_map.get(task.case_id),
            "client_id": task.client_id,
            "year_no": task.year_no,
            "due_date": task.due_date,
            "client_instruction": task.client_instruction,
            "instruction_date": task.instruction_date,
            "notice_status": task.notice_status,
            "notice_sent_date": task.notice_sent_date,
            "status": task.status,
            "remark": task.remark,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "gov_fee_amt": task.gov_fee_amt,
            "service_fee_amt": task.service_fee_amt,
            "notify_count": task.notify_count,
            "pay_next_year": task.pay_next_year,
            "draft_generated": task.draft_generated,
            "notice_sent": task.notice_sent,
            "is_overdue": task.due_date < date.today() and task.status == "OPEN",
            **_annuity_deadline_preview_fields(task.year_no),
        }
        for task in tasks
    ]
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "summary": summary,
    }


@router.put("/annuity/tasks/{task_id}/instruction", summary="Update annuity task instruction")
def put_annuity_task_instruction(
    task_id: int,
    payload: AnnuityInstructionUpdateIn,
    _perm: None = Depends(require_perm("AnnuityTask.Action")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    task = update_annuity_task_instruction(
        db,
        task_id=task_id,
        instruction=payload.instruction,
        instruction_date=payload.instruction_date,
    )
    return {
        "id": task.id,
        "case_id": task.case_id,
        "client_id": task.client_id,
        "year_no": task.year_no,
        "due_date": task.due_date,
        "client_instruction": task.client_instruction,
        "instruction_date": task.instruction_date,
        "notice_status": task.notice_status,
        "notice_sent_date": task.notice_sent_date,
        "status": task.status,
        "remark": task.remark,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.post("/annuity/tasks/generate-drafts", summary="Generate fee drafts from annuity tasks")
def post_annuity_generate_drafts(
    payload: AnnuityGenerateDraftsIn,
    _perm: None = Depends(require_perm("AnnuityTask.Action")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return generate_fee_drafts_from_annuity_tasks(
        db,
        task_ids=payload.task_ids,
        pay_next_year=payload.pay_next_year,
        currency=payload.currency,
    )


@router.post(
    "/annuity/tasks/generate",
    status_code=status.HTTP_201_CREATED,
    summary="Generate annuity tasks for a case",
)
def generate_annuity_tasks_endpoint(
    payload: AnnuityTaskGenerateIn,
    _perm: None = Depends(require_perm("AnnuityTask.Action")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Generate multi-year annuity tasks for a GRANTED case.

    **Auth**: Bearer JWT
    **Permission**: AnnuityTask.Action
    """
    from app.modules.annuity.service import generate_annuity_tasks_for_case

    result = generate_annuity_tasks_for_case(db, case_id=payload.case_id)
    db.commit()
    return result


@router.post("/pay-lists/from-fee-items", summary="Create pay list from fee items")
def post_pay_list_from_fee_items(
    payload: PayListFromFeeItemsIn,
    _perm: None = Depends(require_perm("PayList.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        result = create_pay_list_from_fee_items(
            db,
            fee_item_ids=payload.fee_item_ids,
            planned_pay_date=payload.planned_pay_date,
            remark=payload.remark,
            actor_id=current_user.id,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.get("/pay-lists", summary="List pay lists")
def get_pay_lists(
    pay_list_no: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    planned_pay_date_from: date | None = Query(default=None),
    planned_pay_date_to: date | None = Query(default=None),
    currency: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    app_no: str | None = Query(default=None),
    list_type: str | None = Query(default=None),
    flow_dir: str | None = Query(default=None),
    fee_code: str | None = Query(default=None),
    voucher_no: str | None = Query(default=None),
    invoice_no: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("PayList.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List pay-list headers with supported read-only filters and pagination."""
    filters = {
        "pay_list_no": pay_list_no,
        "client_id": client_id,
        "status": status,
        "planned_pay_date_from": planned_pay_date_from,
        "planned_pay_date_to": planned_pay_date_to,
        "currency": currency,
        "case_no": case_no,
        "app_no": app_no,
        "list_type": list_type,
        "flow_dir": flow_dir,
        "fee_code": fee_code,
        "voucher_no": voucher_no,
        "invoice_no": invoice_no,
    }
    pay_lists, total = list_pay_lists(db, filters=filters, page=page, page_size=page_size)

    client_ids = {pay_list.client_id for pay_list in pay_lists if pay_list.client_id}
    client_name_map: dict[str, str] = {}
    if client_ids:
        from app.modules.masterdata.clients.models import Client

        clients = db.query(Client.id, Client.name_cn).filter(Client.id.in_(client_ids)).all()
        client_name_map = {client.id: client.name_cn for client in clients}

    items = [
        {
            "id": pay_list.id,
            "pay_list_no": pay_list.pay_list_no,
            "client_id": pay_list.client_id,
            "client_name": client_name_map.get(pay_list.client_id),
            "status": pay_list.status,
            "currency": pay_list.currency,
            "planned_pay_date": pay_list.planned_pay_date,
            "paid_date": pay_list.paid_date,
            "total_amount": str(pay_list.total_amount),
            "remark": pay_list.remark,
            "list_type": pay_list.list_type,
            "flow_dir": pay_list.flow_dir,
            "invoice_no_from": pay_list.invoice_no_from,
            "invoice_no_to": pay_list.invoice_no_to,
            "created_at": pay_list.created_at,
            "updated_at": pay_list.updated_at,
            "created_by": pay_list.created_by,
            "updated_by": pay_list.updated_by,
        }
        for pay_list in pay_lists
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.get("/pay-lists/{pay_list_id}", summary="Get pay list detail")
def get_pay_list(
    pay_list_id: int,
    _perm: None = Depends(require_perm("PayList.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return get_pay_list_detail(db, pay_list_id=pay_list_id)


@router.post(
    "/pay-lists/{pay_list_id}/export",
    summary="Export pay list to Excel",
    response_class=Response,
    responses={
        200: {
            "content": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}},
            "description": "Excel export generated",
        }
    },
)
def post_pay_list_export(
    pay_list_id: int,
    _perm: None = Depends(require_perm("PayList.Export")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> Response:
    pay_list = db.get(PayList, pay_list_id)
    if pay_list is None:
        raise_business_error("PAY_LIST_NOT_FOUND", "Pay list not found", status_code=404)
    if (pay_list.status or "").strip().upper() != "DRAFT":
        raise_business_error(
            "PAY_LIST_STATE_CONFLICT",
            "Pay list can only be exported from DRAFT status",
            details={"status": pay_list.status},
            status_code=409,
        )

    export_result = None
    try:
        export_result = export_internal_pay_list(
            ExportInternalPayListCommand(
                pay_list_id=pay_list_id,
                actor_id=current_user.id,
                idempotency_key=f"pay-list-internal-export:http-v1:{pay_list_id}",
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        if export_result is not None and not export_result.reused:
            compensate_internal_pay_list_export(export_result.managed_storage_path)
        raise
    return Response(
        content=export_result.content,
        media_type=export_result.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{export_result.filename}"',
        },
    )


@router.post(
    "/pay-lists/{pay_list_id}/official-workbook",
    summary="Generate official payment workbook",
    response_class=Response,
    responses={
        200: {
            "content": {"application/vnd.ms-excel.sheet.macroEnabled.12": {}},
            "description": "Existing official payment workbook returned",
        },
        201: {
            "content": {"application/vnd.ms-excel.sheet.macroEnabled.12": {}},
            "description": "Official payment workbook generated",
        },
    },
)
def post_official_payment_workbook(
    pay_list_id: int,
    payload: OfficialPaymentWorkbookGenerateIn,
    _perm: None = Depends(require_perm("PayList.Export")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> Response:
    result = None
    try:
        result = generate_official_payment_workbook(
            GenerateOfficialPaymentWorkbookCommand(
                pay_list_id=pay_list_id,
                rows=tuple(OfficialPaymentRow(**row.model_dump()) for row in payload.rows),
                actor_id=str(current_user.id),
                idempotency_key=payload.idempotency_key,
                generated_at=_official_workbook_utcnow(),
                runtime_profile=_official_workbook_runtime_profile(),
            ),
            db,
        )
        response = Response(
            status_code=201 if result.disposition == "CREATED" else 200,
            content=result.content,
            media_type=result.content_type,
            headers={
                "Content-Disposition": (
                    "attachment; filename*=UTF-8''" + quote(result.filename, safe="")
                ),
                "X-FPMS-Artifact-Id": quote(result.artifact_id, safe=""),
                "X-FPMS-Content-SHA256": quote(result.content_sha256, safe=""),
                "X-FPMS-Template-Version": quote(result.template_version, safe=""),
                "X-FPMS-Template-Content-SHA256": quote(
                    result.template_content_hash,
                    safe="",
                ),
                "X-FPMS-Workbook-Input-Version-Id": quote(
                    result.workbook_input_version_id,
                    safe="",
                ),
                "X-FPMS-Workbook-Disposition": quote(result.disposition, safe=""),
                "X-FPMS-Generated-Status": quote(result.generated_status, safe=""),
            },
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        if result is not None and result.disposition == "CREATED":
            try:
                compensate_official_payment_workbook(result.managed_storage_path)
            except Exception as compensation_error:
                raise compensation_error from exc
        raise
    return response


@router.post(
    "/pay-lists/{pay_list_id}/official-workbook/acceptance",
    status_code=status.HTTP_201_CREATED,
    response_model=OfficialWorkbookAcceptanceOut,
    summary="Record official workbook acceptance evidence",
)
def post_official_workbook_acceptance(
    pay_list_id: int,
    payload: OfficialWorkbookAcceptanceIn,
    response: Response,
    _perm: None = Depends(require_perm("Fee.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> OfficialWorkbookAcceptanceOut:
    try:
        result = record_official_workbook_acceptance(
            RecordOfficialWorkbookAcceptanceCommand(
                pay_list_id=pay_list_id,
                artifact_id=payload.artifact_id,
                evidence_ref=payload.evidence_ref,
                evidence_sha256=payload.evidence_sha256,
                accepted_at=payload.accepted_at,
                actor_id=str(current_user.id),
                idempotency_key=payload.idempotency_key,
                runtime_profile=_official_workbook_runtime_profile(),
            ),
            db,
        )
        output = OfficialWorkbookAcceptanceOut.model_validate(result)
        db.commit()
    except Exception:
        db.rollback()
        raise
    if result.disposition == "REUSED":
        response.status_code = status.HTTP_200_OK
    return output


@router.post("/pay-lists/{pay_list_id}/mark-paid", summary="Mark pay list paid")
def post_pay_list_mark_paid(
    pay_list_id: int,
    payload: PayListMarkPaidIn,
    _perm: None = Depends(require_perm("Billing.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return mark_pay_list_paid(
        db,
        pay_list_id=pay_list_id,
        paid_date=payload.paid_date,
        actor_id=current_user.id,
    )


@router.post(
    "/pay-lists",
    status_code=status.HTTP_201_CREATED,
    summary="Create historical pay list",
)
def post_pay_lists(
    payload: HistoricalPayListCreateIn,
    _perm: None = Depends(require_perm("PayList.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return create_historical_pay_list(
        db,
        client_id=payload.client_id,
        currency=payload.currency,
        planned_pay_date=payload.planned_pay_date,
        remark=payload.remark,
        list_type=payload.list_type,
        flow_dir=payload.flow_dir,
        invoice_no_from=payload.invoice_no_from,
        invoice_no_to=payload.invoice_no_to,
        actor_id=current_user.id,
    )


@router.post("/gov-payments", summary="Register official payment")
def post_gov_payments(
    payload: GovPaymentCreateIn,
    _perm: None = Depends(require_perm("GovPayment.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return register_gov_payment(
        db,
        pay_list_id=payload.pay_list_id,
        fee_item_id=payload.fee_item_id,
        paid_date=payload.paid_date,
        paid_amount=payload.paid_amount,
        official_receipt_no=payload.official_receipt_no,
        remark=payload.remark,
        paid_currency=payload.paid_currency,
        voucher_no=payload.voucher_no,
        invoice_no=payload.invoice_no,
    )


@router.post("/pay-lists/{pay_list_id}/manual-items", summary="Add manual gov payment item")
def post_pay_list_manual_items(
    pay_list_id: int,
    payload: ManualGovPaymentCreateIn,
    _perm: None = Depends(require_perm("GovPayment.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return add_manual_gov_payment(
        db,
        pay_list_id=pay_list_id,
        case_id=payload.case_id,
        fee_item_id=payload.fee_item_id,
        paid_date=payload.paid_date,
        paid_amount=payload.paid_amount,
        official_receipt_no=payload.official_receipt_no,
        remark=payload.remark,
        fee_code=payload.fee_code,
        year_no=payload.year_no,
        paid_currency=payload.paid_currency,
        voucher_no=payload.voucher_no,
        invoice_no=payload.invoice_no,
        actor_id=current_user.id,
    )
