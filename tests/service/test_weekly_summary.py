from datetime import date
from pathlib import Path

import pytest

from app.constants import NO_ITEMS_TEXT, TEMPLATE_FILENAME
from service.weekly_summary import (
    WeeklySummaryError,
    collect_entries,
    create_weekly_summary,
    summary_file_path,
)

START = date(2026, 8, 5)
END = date(2026, 8, 7)

EXPECTED_MARKDOWN = """---
type: weekly
week: 20260805_20260807_weekly
tags:
  - 週次振り返り
---

# 業務日誌まとめ

期間:20260805 ｰ 20260807

## うまくいったこと

- クラーク業務依頼を引き受けた。

## 課題と対策

- 事後検証手順作成（完了条件：8/15）
- 確認表の整備

## 学びと気づき

- ベータ版には手を出さない方が効率が良い。
- CDのオーダーを初めて依頼した。

## タグ別ログ

### #対人

- 見学の相談を受けた。

### #トラブル

- オペ録が見当たらないと報告があった。
- スリット画像が黄色いままだった。

### タグ件数

| カテゴリ | 件数 |
| --- | --- |
| #トラブル | 2 |
| #対人 | 1 |
"""


def test_summary_file_path_開始日と終了日からファイル名を組み立てる(tmp_path: Path) -> None:
    assert summary_file_path(tmp_path, START, END).name == "20260805_20260807_weekly.md"


def test_collect_entries_存在する日誌のみ日付順に集める(daily_path: Path) -> None:
    entries = collect_entries(daily_path, START, END)

    assert [entry.date for entry in entries] == [date(2026, 8, 5), date(2026, 8, 7)]


def test_collect_entries_日誌フォルダがない場合はエラー(tmp_path: Path) -> None:
    with pytest.raises(WeeklySummaryError):
        collect_entries(tmp_path / "missing", START, END)


def test_create_weekly_summary_テンプレート書式で出力する(
    templates_path: Path, daily_path: Path, weekly_path: Path
) -> None:
    output_path = create_weekly_summary(templates_path, daily_path, weekly_path, START, END)

    assert output_path == weekly_path / "20260805_20260807_weekly.md"
    assert output_path.read_text(encoding="utf-8") == EXPECTED_MARKDOWN


def test_create_weekly_summary_未知の見出しはテンプレート本文を残す(
    templates_path: Path, daily_path: Path, weekly_path: Path
) -> None:
    template_file = templates_path / TEMPLATE_FILENAME
    template_file.write_text(
        template_file.read_text(encoding="utf-8") + "\n## 備考\n記入欄\n", encoding="utf-8"
    )

    output_path = create_weekly_summary(templates_path, daily_path, weekly_path, START, END)

    assert output_path.read_text(encoding="utf-8").endswith("## 備考\n\n記入欄\n")


def test_create_weekly_summary_該当項目がない場合は該当なしと出力する(
    templates_path: Path, daily_path: Path, weekly_path: Path
) -> None:
    output_path = create_weekly_summary(
        templates_path, daily_path, weekly_path, date(2026, 8, 7), date(2026, 8, 7)
    )

    assert f"## うまくいったこと\n\n{NO_ITEMS_TEXT}" in output_path.read_text(encoding="utf-8")


def test_create_weekly_summary_期間内に日誌がない場合はエラー(
    templates_path: Path, daily_path: Path, weekly_path: Path
) -> None:
    with pytest.raises(WeeklySummaryError):
        create_weekly_summary(
            templates_path, daily_path, weekly_path, date(2026, 9, 1), date(2026, 9, 2)
        )


def test_create_weekly_summary_テンプレートがない場合はエラー(
    tmp_path: Path, daily_path: Path, weekly_path: Path
) -> None:
    with pytest.raises(WeeklySummaryError):
        create_weekly_summary(tmp_path / "empty", daily_path, weekly_path, START, END)
