"""日誌を期間で集約し、テンプレート書式のまとめを生成する。"""

from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

from app.constants import (
    DAILY_DATE_FORMAT,
    DISPLAY_DATE_FORMAT,
    ERROR_DAILY_DIR_NOT_FOUND,
    ERROR_NO_DAILY_FILES,
    ERROR_TEMPLATE_NOT_FOUND,
    NO_ITEMS_TEXT,
    PLACEHOLDER_END_DATE,
    PLACEHOLDER_START_DATE,
    PLACEHOLDER_TITLE,
    SECTION_ISSUES,
    SECTION_LEARNINGS,
    SECTION_SUCCESSES,
    SECTION_TAG_LOG,
    SUBSECTION_TAG_COUNT,
    SUMMARY_DATE_FORMAT,
    TAG_COUNT_TABLE_HEADER,
    TARGET_TAGS,
    TEMPLATE_FILENAME,
)
from service.daily_parser import DailyEntry, extract_preamble, parse_daily, split_sections


class WeeklySummaryError(Exception):
    """まとめ作成を継続できない業務エラー。"""


def summary_file_path(summary_path: Path, start: date, end: date) -> Path:
    return summary_path / f"{summary_title(start, end)}.md"


def summary_title(start: date, end: date) -> str:
    return (
        f"{start.strftime(SUMMARY_DATE_FORMAT)}"
        f"_{end.strftime(SUMMARY_DATE_FORMAT)}_summary"
    )


def collect_entries(daily_path: Path, start: date, end: date) -> list[DailyEntry]:
    if not daily_path.is_dir():
        raise WeeklySummaryError(ERROR_DAILY_DIR_NOT_FOUND.format(path=daily_path))

    entries: list[DailyEntry] = []
    current = start
    while current <= end:
        file_path = daily_path / f"{current.strftime(DAILY_DATE_FORMAT)}.md"
        if file_path.is_file():
            entries.append(parse_daily(file_path))
        current += timedelta(days=1)
    return entries


def build_markdown(template_text: str, entries: list[DailyEntry], start: date, end: date) -> str:
    preamble = _fill_placeholders(extract_preamble(template_text), start, end)
    blocks = [preamble.strip()]
    for name, template_body in split_sections(template_text).items():
        body = _build_section_body(name, template_body, entries)
        blocks.append(f"## {name}\n\n{body}")
    return "\n\n".join(blocks) + "\n"


def create_weekly_summary(
    templates_path: Path,
    daily_path: Path,
    summary_path: Path,
    start: date,
    end: date,
) -> Path:
    entries = collect_entries(daily_path, start, end)
    if not entries:
        raise WeeklySummaryError(ERROR_NO_DAILY_FILES)

    template_file = templates_path / TEMPLATE_FILENAME
    if not template_file.is_file():
        raise WeeklySummaryError(ERROR_TEMPLATE_NOT_FOUND.format(path=template_file))

    markdown = build_markdown(template_file.read_text(encoding="utf-8"), entries, start, end)
    summary_path.mkdir(parents=True, exist_ok=True)
    output_path = summary_file_path(summary_path, start, end)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def _fill_placeholders(preamble: str, start: date, end: date) -> str:
    return (
        preamble.replace(PLACEHOLDER_TITLE, summary_title(start, end))
        .replace(PLACEHOLDER_START_DATE, start.strftime(DISPLAY_DATE_FORMAT))
        .replace(PLACEHOLDER_END_DATE, end.strftime(DISPLAY_DATE_FORMAT))
    )


def _build_section_body(name: str, template_body: list[str], entries: list[DailyEntry]) -> str:
    if name == SECTION_SUCCESSES:
        return _bullet_list(item for entry in entries for item in entry.successes)
    if name == SECTION_ISSUES:
        return _bullet_list(item for entry in entries for item in entry.issues)
    if name == SECTION_LEARNINGS:
        return _bullet_list(item for entry in entries for item in entry.learnings)
    if name == SECTION_TAG_LOG:
        return _build_tag_log(entries)
    return "\n".join(template_body).strip()


def _bullet_list(items: Iterable[str]) -> str:
    lines = [f"- {item}" for item in items]
    return "\n".join(lines) if lines else NO_ITEMS_TEXT


def _build_tag_log(entries: list[DailyEntry]) -> str:
    logs = [log for entry in entries for log in entry.logs]
    if not logs:
        return NO_ITEMS_TEXT

    blocks: list[str] = []
    for tag in TARGET_TAGS:
        texts = [log.text for log in logs if log.tag == tag]
        if texts:
            blocks.append(f"### {tag}\n\n{_bullet_list(texts)}")
    blocks.append(_build_tag_count_table(Counter(log.tag for log in logs)))
    return "\n\n".join(blocks)


def _build_tag_count_table(counts: Counter[str]) -> str:
    # 件数の多い順、同数はテンプレート記載のタグ順
    ordered_tags = sorted(
        (tag for tag in TARGET_TAGS if counts[tag]),
        key=lambda tag: (-counts[tag], TARGET_TAGS.index(tag)),
    )
    rows = "\n".join(f"| {tag} | {counts[tag]} |" for tag in ordered_tags)
    return f"### {SUBSECTION_TAG_COUNT}\n\n{TAG_COUNT_TABLE_HEADER}\n{rows}"
