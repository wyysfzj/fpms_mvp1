from __future__ import annotations

from datetime import date, datetime
from io import BytesIO
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

COMMISSION_REPORT_EXPORT_MIME_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


def _column_name(index: int) -> str:
    result = ""
    current = index
    while current > 0:
        current, remainder = divmod(current - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _normalize_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _cell_xml(row_no: int, column_no: int, value: object) -> str:
    text = escape(_normalize_value(value))
    ref = f"{_column_name(column_no)}{row_no}"
    return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{text}</t></is></c>'


def _sheet_xml(rows: list[list[object]]) -> bytes:
    row_xml_parts: list[str] = []
    for row_no, row in enumerate(rows, start=1):
        cells = "".join(
            _cell_xml(row_no, column_no, value) for column_no, value in enumerate(row, start=1)
        )
        row_xml_parts.append(f'<row r="{row_no}">{cells}</row>')

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheetData>{''.join(row_xml_parts)}</sheetData>"
        "</worksheet>"
    )
    return sheet_xml.encode("utf-8")


def build_commission_settlement_report_xlsx(*, report: dict[str, object]) -> bytes:
    summary = report.get("summary") or {}
    by_agent = report.get("by_agent") or []
    by_case = report.get("by_case") or []
    by_time = report.get("by_time") or []
    details = report.get("details") or []

    rows: list[list[object]] = [
        ["提成结算报表"],
        [],
        ["统计摘要"],
        ["明细总数", summary.get("line_count", 0)],
        ["结算批次数", summary.get("settlement_count", 0)],
        ["代理人数", summary.get("agent_count", 0)],
        ["案件数", summary.get("case_count", 0)],
        ["提成总额", summary.get("total_amount", "0.00")],
        [],
        ["按代理人统计"],
        ["代理人编号", "明细数", "总额"],
    ]

    for item in by_agent:
        rows.append(
            [item.get("agent_id", ""), item.get("line_count", 0), item.get("total_amount", "0.00")]
        )

    rows.extend([[], ["按案件统计"], ["案件编号", "明细数", "总额"]])
    for item in by_case:
        rows.append(
            [item.get("case_id", ""), item.get("line_count", 0), item.get("total_amount", "0.00")]
        )

    rows.extend([[], ["按时间统计"], ["时间分桶", "明细数", "总额"]])
    for item in by_time:
        rows.append(
            [
                item.get("time_bucket", ""),
                item.get("line_count", 0),
                item.get("total_amount", "0.00"),
            ]
        )

    rows.extend(
        [
            [],
            ["明细列表"],
            [
                "批次编号",
                "批次号",
                "提成编号",
                "代理人编号",
                "案件编号",
                "金额",
                "币种",
                "批次状态",
                "明细状态",
                "S1完成",
                "S2完成",
                "可结算",
                "可结算日期",
                "结算期间开始",
                "结算期间结束",
                "创建时间",
            ],
        ]
    )
    for item in details:
        rows.append(
            [
                item.get("settlement_id", ""),
                item.get("settlement_no", ""),
                item.get("commission_id", ""),
                item.get("agent_id", ""),
                item.get("case_id", ""),
                item.get("amount", "0.00"),
                item.get("currency", ""),
                item.get("settlement_status", ""),
                item.get("line_status", ""),
                "是" if item.get("s1_done") else "否",
                "是" if item.get("s2_done") else "否",
                "是" if item.get("is_settleable") else "否",
                item.get("settleable_date", ""),
                item.get("period_from", ""),
                item.get("period_to", ""),
                item.get("created_at", ""),
            ]
        )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<sheets>"
        '<sheet name="提成结算报表" sheetId="1" r:id="rId1"/>'
        "</sheets>"
        "</workbook>"
    ).encode("utf-8")

    workbook_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        "</Relationships>"
    ).encode("utf-8")

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    ).encode("utf-8")

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>"
    ).encode("utf-8")

    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml)
        archive.writestr("_rels/.rels", rels_xml)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        archive.writestr("xl/worksheets/sheet1.xml", _sheet_xml(rows))
    return buffer.getvalue()
