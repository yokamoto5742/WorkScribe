"""01_Daily のマークダウン日誌を解析する。"""

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from app.constants import (
    DAILY_DATE_FORMAT,
    SECTION_DAILY_LOG,
    SECTION_ISSUES,
    SECTION_LEARNINGS,
    SECTION_SUCCESSES,
    TARGET_TAGS,
)

_CHECKBOX_PATTERN = re.compile(r"^\[[ xX]\]\s*")
_TAG_PATTERN = re.compile(r"^(#\S+)\s+(.*)$")


@dataclass(frozen=True)
class TaggedLog:
    tag: str
    text: str


@dataclass(frozen=True)
class DailyEntry:
    date: date
    logs: list[TaggedLog]
    successes: list[str]
    issues: list[str]
    learnings: list[str]


def split_sections(text: str) -> dict[str, list[str]]:
    """`## 見出し` 単位で本文行を分割する。最初の見出しより前の行は含めない。"""
    sections: dict[str, list[str]] = {}
    current_body: list[str] | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current_body = []
            sections[line[3:].strip()] = current_body
        elif current_body is not None:
            current_body.append(line)
    return sections


def extract_preamble(text: str) -> str:
    """最初の `## 見出し` より前の部分を返す。"""
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            break
        lines.append(line)
    return "\n".join(lines)


def extract_bullets(lines: list[str], strip_checkbox: bool = False) -> list[str]:
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        item = stripped[2:].strip()
        if strip_checkbox:
            item = _CHECKBOX_PATTERN.sub("", item)
        if item:
            items.append(item)
    return items


def parse_daily(file_path: Path) -> DailyEntry:
    sections = split_sections(file_path.read_text(encoding="utf-8"))
    return DailyEntry(
        date=datetime.strptime(file_path.stem, DAILY_DATE_FORMAT).date(),
        logs=_extract_logs(sections.get(SECTION_DAILY_LOG, [])),
        successes=extract_bullets(sections.get(SECTION_SUCCESSES, [])),
        issues=extract_bullets(sections.get(SECTION_ISSUES, []), strip_checkbox=True),
        learnings=extract_bullets(sections.get(SECTION_LEARNINGS, [])),
    )


def _extract_logs(lines: list[str]) -> list[TaggedLog]:
    logs: list[TaggedLog] = []
    for item in extract_bullets(lines):
        matched = _TAG_PATTERN.match(item)
        if matched and matched.group(1) in TARGET_TAGS:
            logs.append(TaggedLog(tag=matched.group(1), text=matched.group(2).strip()))
    return logs
