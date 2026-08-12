from datetime import date
from pathlib import Path

import pytest

from service.weekly_review import create_weekly_review, review_file_path
from service.weekly_summary import WeeklySummaryError

START = date(2026, 8, 3)
END = date(2026, 8, 9)

EXPECTED_MARKDOWN = """---
type: weekly
week: 20260803_20260809_weekly
tags:
  - 週次振り返り
---

# 1週間の振り返り

期間:2026年8月3日 ｰ 2026年8月9日

### 優れた仕事は何か
>自分の強みから生まれた成果を書く
-

### お粗末な仕事や失敗した仕事は何か

事実：
原因：
次のアクション：

### 改善すべきことは何か

対象：{例：予定の詰め込み、調査の拡散、連絡の遅れ、レビュー不足}
原因：
"""


def test_review_file_path_開始日と終了日からファイル名を組み立てる(tmp_path: Path) -> None:
    assert review_file_path(tmp_path, START, END).name == "20260803_20260809_weekly.md"


def test_create_weekly_review_テンプレート書式の雛形を出力する(
    templates_path: Path, weekly_path: Path
) -> None:
    output_path = create_weekly_review(templates_path, weekly_path, START, END)

    assert output_path == weekly_path / "20260803_20260809_weekly.md"
    assert output_path.read_text(encoding="utf-8") == EXPECTED_MARKDOWN


def test_create_weekly_review_プレースホルダでない波括弧は残す(
    templates_path: Path, weekly_path: Path
) -> None:
    output_path = create_weekly_review(templates_path, weekly_path, START, END)

    assert "対象：{例：予定の詰め込み、調査の拡散、連絡の遅れ、レビュー不足}" in output_path.read_text(
        encoding="utf-8"
    )


def test_create_weekly_review_保存先フォルダがなければ作成する(
    templates_path: Path, weekly_path: Path
) -> None:
    assert not weekly_path.exists()

    create_weekly_review(templates_path, weekly_path, START, END)

    assert weekly_path.is_dir()


def test_create_weekly_review_テンプレートがない場合はエラー(
    tmp_path: Path, weekly_path: Path
) -> None:
    with pytest.raises(WeeklySummaryError):
        create_weekly_review(tmp_path / "empty", weekly_path, START, END)
