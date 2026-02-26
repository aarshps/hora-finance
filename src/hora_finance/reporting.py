from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re

from .sheets import SheetsError, fetch_sheet_rows


_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%b %d %Y",
    "%d %b %Y",
)
_AMOUNT_QUANTIZE = Decimal("0.01")


@dataclass(frozen=True)
class ReportMeta:
    spreadsheet_id: str
    used_range: str
    transaction_count: int


def _normalize_header(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower().strip()).strip("_")


def _find_header_index(headers: list[str], candidates: set[str]) -> int | None:
    for idx, header in enumerate(headers):
        if _normalize_header(header) in candidates:
            return idx
    return None


def _cell(row: list[str], idx: int | None) -> str:
    if idx is None or idx >= len(row):
        return ""
    return str(row[idx]).strip()


def _parse_amount(raw: str) -> Decimal | None:
    value = raw.strip()
    if not value:
        return None

    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1]
    value = value.replace(",", "")
    value = re.sub(r"[^0-9.\-]", "", value)
    if not value:
        return None

    try:
        parsed = Decimal(value)
    except InvalidOperation:
        return None
    return -parsed if negative else parsed


def _parse_month(raw: str) -> str:
    value = raw.strip()
    if not value:
        return "Unknown"

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m")
    except ValueError:
        pass

    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m")
        except ValueError:
            continue
    return "Unknown"


def _apply_direction(amount: Decimal, direction: str) -> Decimal:
    lowered = direction.lower()
    expense_markers = ("expense", "debit", "outflow", "withdrawal")
    income_markers = ("income", "credit", "inflow", "deposit")

    if any(marker in lowered for marker in expense_markers) and amount > 0:
        return -amount
    if any(marker in lowered for marker in income_markers) and amount < 0:
        return -amount
    return amount


def _format_decimal(value: Decimal) -> str:
    return f"{value.quantize(_AMOUNT_QUANTIZE):,.2f}"


def _build_report(
    rows: list[list[str]],
    spreadsheet_id: str,
    used_range: str,
) -> tuple[str, ReportMeta]:
    headers = rows[0] if rows else []
    if not headers:
        raise SheetsError("The selected range is empty.")

    amount_idx = _find_header_index(
        headers,
        {
            "amount",
            "value",
            "total",
            "debit_credit_amount",
            "net_amount",
        },
    )
    if amount_idx is None:
        raise SheetsError(
            "Could not find an amount column. Add a header like 'Amount' or 'Value'."
        )

    date_idx = _find_header_index(headers, {"date", "transaction_date", "posted_date"})
    category_idx = _find_header_index(headers, {"category", "type", "group"})
    description_idx = _find_header_index(headers, {"description", "details", "memo", "note"})
    direction_idx = _find_header_index(
        headers,
        {"direction", "kind", "transaction_type", "income_expense", "debit_credit_type"},
    )

    total_income = Decimal("0")
    total_expense = Decimal("0")
    monthly_net: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    category_income: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    category_expense: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    top_transactions: list[tuple[Decimal, str, str, str, Decimal]] = []
    transaction_count = 0

    for row in rows[1:]:
        amount = _parse_amount(_cell(row, amount_idx))
        if amount is None:
            continue

        direction = _cell(row, direction_idx)
        if direction:
            amount = _apply_direction(amount, direction)

        category = _cell(row, category_idx) or "Uncategorized"
        description = _cell(row, description_idx) or "-"
        month = _parse_month(_cell(row, date_idx))

        if amount >= 0:
            total_income += amount
            category_income[category] += amount
        else:
            total_expense += -amount
            category_expense[category] += -amount

        monthly_net[month] += amount
        top_transactions.append((abs(amount), month, category, description, amount))
        transaction_count += 1

    net = total_income - total_expense
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Finance Report",
        "",
        f"- Generated at: {now_utc}",
        f"- Spreadsheet ID: `{spreadsheet_id}`",
        f"- Range: `{used_range}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Transactions | {transaction_count} |",
        f"| Total Income | {_format_decimal(total_income)} |",
        f"| Total Expense | {_format_decimal(total_expense)} |",
        f"| Net | {_format_decimal(net)} |",
        "",
        "## Monthly Net",
        "",
        "| Month | Net |",
        "|---|---:|",
    ]

    if monthly_net:
        for month in sorted(monthly_net.keys()):
            lines.append(f"| {month} | {_format_decimal(monthly_net[month])} |")
    else:
        lines.append("| - | 0.00 |")

    lines.extend(
        [
            "",
            "## Category Breakdown",
            "",
            "| Category | Income | Expense | Net |",
            "|---|---:|---:|---:|",
        ]
    )

    categories = sorted(set(category_income.keys()) | set(category_expense.keys()))
    if categories:
        for category in categories:
            income = category_income[category]
            expense = category_expense[category]
            lines.append(
                f"| {category} | {_format_decimal(income)} | "
                f"{_format_decimal(expense)} | {_format_decimal(income - expense)} |"
            )
    else:
        lines.append("| Uncategorized | 0.00 | 0.00 | 0.00 |")

    lines.extend(
        [
            "",
            "## Top Transactions",
            "",
            "| Month | Category | Description | Amount |",
            "|---|---|---|---:|",
        ]
    )
    if top_transactions:
        top_transactions.sort(key=lambda item: item[0], reverse=True)
        for _, month, category, description, amount in top_transactions[:10]:
            lines.append(
                f"| {month} | {category} | {description} | {_format_decimal(amount)} |"
            )
    else:
        lines.append("| - | - | - | 0.00 |")

    report = "\n".join(lines).strip() + "\n"
    return report, ReportMeta(
        spreadsheet_id=spreadsheet_id,
        used_range=used_range,
        transaction_count=transaction_count,
    )


def generate_report_from_google_sheet(
    credentials_json: str,
    spreadsheet_id: str,
    value_range: str | None = None,
) -> tuple[str, ReportMeta]:
    used_range, rows = fetch_sheet_rows(
        credentials_json=credentials_json,
        spreadsheet_id=spreadsheet_id,
        value_range=value_range,
    )
    return _build_report(rows=rows, spreadsheet_id=spreadsheet_id, used_range=used_range)


def save_report(
    report_markdown: str,
    reports_dir: Path,
    spreadsheet_id: str,
    output_path: Path | None = None,
) -> Path:
    if output_path is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        safe_sheet = (
            re.sub(r"[^A-Za-z0-9_-]+", "_", spreadsheet_id).strip("_")[:24]
            or "sheet"
        )
        output_path = reports_dir / f"finance-report-{safe_sheet}-{ts}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_markdown, encoding="utf-8")
    return output_path
