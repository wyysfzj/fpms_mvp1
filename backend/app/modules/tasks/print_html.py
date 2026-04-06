from __future__ import annotations

from datetime import date, datetime
from html import escape

from app.modules.tasks.schemas import TaskListItemOut, TaskSpecialSearchItemOut

TASK_LIST_PRINT_MIME_TYPE = "text/html; charset=utf-8"


def _normalize_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def build_task_list_print_html(
    *,
    title: str,
    items: list[TaskListItemOut],
) -> str:
    rows = []
    for item in items:
        status = item.status.value if hasattr(item.status, "value") else item.status
        rows.append(
            "<tr>"
            f"<td>{escape(_normalize_value(item.id))}</td>"
            f"<td>{escape(_normalize_value(item.title))}</td>"
            f"<td>{escape(_normalize_value(item.case_no or ''))}</td>"
            f"<td>{escape(_normalize_value(item.client_name or ''))}</td>"
            f"<td>{escape(_normalize_value(status))}</td>"
            f"<td>{escape(_normalize_value(item.due_date or ''))}</td>"
            f"<td>{escape(_normalize_value(item.internal_due_date or ''))}</td>"
            f"<td>{escape(_normalize_value(item.worker_id or ''))}</td>"
            f"<td>{escape(_normalize_value(item.supervisor_id or ''))}</td>"
            "</tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <title>{escape(title)}</title>
    <style>
      body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        margin: 24px;
        color: #1f2937;
      }}
      h1 {{
        margin: 0 0 12px;
        font-size: 24px;
      }}
      .meta {{
        margin-bottom: 16px;
        color: #4b5563;
        font-size: 14px;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
      }}
      th, td {{
        border: 1px solid #d1d5db;
        padding: 8px;
        text-align: left;
        vertical-align: top;
      }}
      th {{
        background: #f3f4f6;
      }}
      @media print {{
        body {{
          margin: 0;
        }}
      }}
    </style>
  </head>
  <body>
    <h1>{escape(title)}</h1>
    <div class="meta">共 {len(items)} 条</div>
    <table>
      <thead>
        <tr>
          <th>任务ID</th>
          <th>标题</th>
          <th>案号</th>
          <th>客户</th>
          <th>状态</th>
          <th>截止日期</th>
          <th>内部期限</th>
          <th>作业人</th>
          <th>监督人</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </body>
</html>"""


def build_task_special_search_print_html(
    *,
    title: str,
    items: list[TaskSpecialSearchItemOut],
) -> str:
    rows = []
    for item in items:
        status = item.status.value if hasattr(item.status, "value") else item.status
        rows.append(
            "<tr>"
            f"<td>{escape(_normalize_value(item.task_code))}</td>"
            f"<td>{escape(_normalize_value(item.task_id))}</td>"
            f"<td>{escape(_normalize_value(item.case_no or ''))}</td>"
            f"<td>{escape(_normalize_value(item.client_name or ''))}</td>"
            f"<td>{escape(_normalize_value(item.title))}</td>"
            f"<td>{escape(_normalize_value(status))}</td>"
            f"<td>{escape(_normalize_value(item.due_date or ''))}</td>"
            f"<td>{'是' if item.is_overdue else '否'}</td>"
            f"<td>{escape(_normalize_value(item.remark or ''))}</td>"
            "</tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <title>{escape(title)}</title>
    <style>
      body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        margin: 24px;
        color: #1f2937;
      }}
      h1 {{
        margin: 0 0 12px;
        font-size: 24px;
      }}
      .meta {{
        margin-bottom: 16px;
        color: #4b5563;
        font-size: 14px;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
      }}
      th, td {{
        border: 1px solid #d1d5db;
        padding: 8px;
        text-align: left;
        vertical-align: top;
      }}
      th {{
        background: #f3f4f6;
      }}
    </style>
  </head>
  <body>
    <h1>{escape(title)}</h1>
    <div class="meta">共 {len(items)} 条</div>
    <table>
      <thead>
        <tr>
          <th>任务编码</th>
          <th>任务ID</th>
          <th>案号</th>
          <th>客户</th>
          <th>标题</th>
          <th>状态</th>
          <th>截止日期</th>
          <th>是否逾期</th>
          <th>备注</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </body>
</html>"""
