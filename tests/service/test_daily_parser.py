from datetime import date
from pathlib import Path

from service.daily_parser import TaggedLog, extract_preamble, parse_daily, split_sections


def test_parse_daily_日付はファイル名から取得する(daily_path: Path) -> None:
    entry = parse_daily(daily_path / "2026-08-05.md")

    assert entry.date == date(2026, 8, 5)


def test_parse_daily_対象タグの行のみログとして抽出する(daily_path: Path) -> None:
    entry = parse_daily(daily_path / "2026-08-05.md")

    assert entry.logs == [
        TaggedLog(tag="#対人", text="見学の相談を受けた。"),
        TaggedLog(tag="#トラブル", text="オペ録が見当たらないと報告があった。"),
    ]


def test_parse_daily_引用行と段落行は抽出しない(daily_path: Path) -> None:
    entry = parse_daily(daily_path / "2026-08-05.md")

    assert entry.successes == ["クラーク業務依頼を引き受けた。"]
    assert entry.learnings == ["ベータ版には手を出さない方が効率が良い。"]


def test_parse_daily_課題と対策はチェックボックス記法を除去する(daily_path: Path) -> None:
    entry = parse_daily(daily_path / "2026-08-05.md")

    assert entry.issues == ["事後検証手順作成（完了条件：8/15）", "確認表の整備"]


def test_parse_daily_空のセクションは空リストになる(daily_path: Path) -> None:
    entry = parse_daily(daily_path / "2026-08-07.md")

    assert entry.successes == []
    assert entry.issues == []


def test_split_sections_見出し順を保持する() -> None:
    sections = split_sections("# 表題\n\n## A\n- 1\n\n## B\n- 2\n")

    assert list(sections) == ["A", "B"]
    assert sections["B"] == ["- 2"]


def test_extract_preamble_最初の見出しより前を返す() -> None:
    assert extract_preamble("---\nkey: v\n---\n\n# 表題\n\n## A\n- 1\n") == "---\nkey: v\n---\n\n# 表題\n"
