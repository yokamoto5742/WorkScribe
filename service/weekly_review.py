"""1週間の振り返りテンプレートから記入用の振り返りファイルを生成する。"""

from datetime import date
from pathlib import Path

from app.constants import (
    ERROR_TEMPLATE_NOT_FOUND,
    REVIEW_TEMPLATE_FILENAME,
    SUMMARY_DATE_FORMAT,
)
from service.weekly_summary import WeeklySummaryError, fill_placeholders


def review_title(start: date, end: date) -> str:
    return (
        f"{start.strftime(SUMMARY_DATE_FORMAT)}"
        f"_{end.strftime(SUMMARY_DATE_FORMAT)}_weekly"
    )


def review_file_path(weekly_path: Path, start: date, end: date) -> Path:
    return weekly_path / f"{review_title(start, end)}.md"


def create_weekly_review(templates_path: Path, weekly_path: Path, start: date, end: date) -> Path:
    template_file = templates_path / REVIEW_TEMPLATE_FILENAME
    if not template_file.is_file():
        raise WeeklySummaryError(ERROR_TEMPLATE_NOT_FOUND.format(path=template_file))

    # 記入欄はそのまま残し、タイトルと期間のみ差し替える
    markdown = fill_placeholders(
        template_file.read_text(encoding="utf-8"), review_title(start, end), start, end
    )
    weekly_path.mkdir(parents=True, exist_ok=True)
    output_path = review_file_path(weekly_path, start, end)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path
