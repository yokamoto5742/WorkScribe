"""四半期レビューテンプレートに対象期間を差し込み、レビューファイルを生成する。"""

import re
from datetime import date
from pathlib import Path

from app.constants import (
    DAILY_DATE_FORMAT,
    ERROR_TEMPLATE_NOT_FOUND,
    QUARTERLY_TEMPLATE_FILENAME,
)
from service.weekly_summary import WeeklySummaryError

FISCAL_YEAR_START_MONTH = 4

DATE_RANGE_PATTERN = re.compile(r"file\.day >= date\([^)]*\) AND file\.day <= date\([^)]*\)")
USAGE_LINE_PATTERN = re.compile(r"^> 使い方：.*\n\n?", re.MULTILINE)


def fiscal_quarter_label(start: date) -> str:
    # 4月始まりの年度。1〜3月は前年度の Q4 になる
    months_from_fiscal_start = (start.month - FISCAL_YEAR_START_MONTH) % 12
    fiscal_year = start.year if start.month >= FISCAL_YEAR_START_MONTH else start.year - 1
    return f"{fiscal_year}Q{months_from_fiscal_start // 3 + 1}"


def quarterly_file_path(quarterly_path: Path, start: date) -> Path:
    return quarterly_path / f"{fiscal_quarter_label(start)}_quarterly.md"


def build_quarterly_markdown(template_text: str, start: date, end: date) -> str:
    start_text = start.strftime(DAILY_DATE_FORMAT)
    end_text = end.strftime(DAILY_DATE_FORMAT)
    replacements = {
        r"^quarter:.*$": f"quarter: {fiscal_quarter_label(start)}",
        r"^period_start:.*$": f"period_start: {start_text}",
        r"^period_end:.*$": f"period_end: {end_text}",
    }
    markdown = template_text
    for pattern, replacement in replacements.items():
        markdown = re.sub(pattern, replacement, markdown, count=1, flags=re.MULTILINE)

    markdown = DATE_RANGE_PATTERN.sub(
        f"file.day >= date({start_text}) AND file.day <= date({end_text})", markdown
    )
    return USAGE_LINE_PATTERN.sub("", markdown)


def create_quarterly_review(
    templates_path: Path, quarterly_path: Path, start: date, end: date
) -> Path:
    template_file = templates_path / QUARTERLY_TEMPLATE_FILENAME
    if not template_file.is_file():
        raise WeeklySummaryError(ERROR_TEMPLATE_NOT_FOUND.format(path=template_file))

    markdown = build_quarterly_markdown(template_file.read_text(encoding="utf-8"), start, end)
    quarterly_path.mkdir(parents=True, exist_ok=True)
    output_path = quarterly_file_path(quarterly_path, start)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path
