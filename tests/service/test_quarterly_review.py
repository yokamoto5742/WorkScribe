from datetime import date
from pathlib import Path

import pytest

from service.quarterly_review import (
    create_quarterly_review,
    fiscal_quarter_label,
    quarterly_file_path,
)
from service.weekly_summary import WeeklySummaryError

START = date(2026, 10, 1)
END = date(2026, 12, 31)

EXPECTED_MARKDOWN = """---
type: quarterly
quarter: 2026Q3
period_start: 2026-10-01
period_end: 2026-12-31
tags:
  - 四半期レビュー
---

# 四半期レビュー

## 1. 全エントリ一覧

```dataview
WHERE file.day >= date(2026-10-01) AND file.day <= date(2026-12-31)
```

## 3. 未回収のまま残った対策

```dataview
TASK
WHERE file.day >= date(2026-10-01) AND file.day <= date(2026-12-31)
WHERE !completed
```
"""


@pytest.mark.parametrize(
    ("start", "expected"),
    [
        (date(2026, 4, 1), "2026Q1"),
        (date(2026, 6, 30), "2026Q1"),
        (date(2026, 7, 1), "2026Q2"),
        (date(2026, 9, 30), "2026Q2"),
        (date(2026, 12, 31), "2026Q3"),
        (date(2027, 1, 1), "2026Q4"),
        (date(2027, 3, 31), "2026Q4"),
    ],
)
def test_fiscal_quarter_label_4月始まりの年度で判定する(start: date, expected: str) -> None:
    assert fiscal_quarter_label(start) == expected


def test_quarterly_file_path_開始日の四半期でファイル名を組み立てる(tmp_path: Path) -> None:
    assert quarterly_file_path(tmp_path, date(2026, 9, 1)).name == "2026Q2_quarterly.md"


def test_create_quarterly_review_期間を差し込み使い方行を削除する(
    templates_path: Path, quarterly_path: Path
) -> None:
    output_path = create_quarterly_review(templates_path, quarterly_path, START, END)

    assert output_path == quarterly_path / "2026Q3_quarterly.md"
    assert output_path.read_text(encoding="utf-8") == EXPECTED_MARKDOWN


def test_create_quarterly_review_四半期をまたぐ期間は開始日の四半期で出力する(
    templates_path: Path, quarterly_path: Path
) -> None:
    output_path = create_quarterly_review(
        templates_path, quarterly_path, date(2026, 9, 15), date(2026, 10, 15)
    )

    assert output_path.name == "2026Q2_quarterly.md"


def test_create_quarterly_review_保存先フォルダがなければ作成する(
    templates_path: Path, quarterly_path: Path
) -> None:
    assert not quarterly_path.exists()

    create_quarterly_review(templates_path, quarterly_path, START, END)

    assert quarterly_path.is_dir()


def test_create_quarterly_review_テンプレートがない場合はエラー(
    tmp_path: Path, quarterly_path: Path
) -> None:
    with pytest.raises(WeeklySummaryError):
        create_quarterly_review(tmp_path / "empty", quarterly_path, START, END)
