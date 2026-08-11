from pathlib import Path

import pytest

from app.constants import TEMPLATE_FILENAME

DAILY_0805 = """---
type: daily
date: 2026-08-05
tags:
  - 業務日誌
---

# 2026-08-05 業務日誌

## 本日のログ
> （ `#移譲 /  #説明 / #評価 / #対人 / #開発 / #トラブル `）

- #対人 見学の相談を受けた。
- #トラブル  オペ録が見当たらないと報告があった。
- #未定義 対象外タグの行。
- タグなしの行。

## うまくいったこと
> 理念の実現、成果が得られたこと、予期せぬ成功など
- クラーク業務依頼を引き受けた。

## 課題と対策

- [ ] 事後検証手順作成（完了条件：8/15）
- [x] 確認表の整備

## 学びと気づき
> 新たな取り組みで得られた知見など
- ベータ版には手を出さない方が効率が良い。

対応内容
箇条書きでない段落行。
"""

DAILY_0807 = """---
type: daily
date: 2026-08-07
tags:
  - 業務日誌
---

# 2026-08-07 業務日誌

## 本日のログ

- #トラブル スリット画像が黄色いままだった。

## うまくいったこと

## 課題と対策

## 学びと気づき

- CDのオーダーを初めて依頼した。
"""

TEMPLATE = """---
type: weekly
week: {{title}}
tags:
  - 週次振り返り
---

# 業務日誌まとめ

期間:{開始日(yyyy年m月d日形式)} ｰ {終了日(yyyy年m月d日形式)}

## うまくいったこと
うまくいったことの記述を日付の若い順番から列挙する。

## 課題と対策
チェックボックスは除く。

## 学びと気づき
学びと気づきの記述を日付の若い順番から列挙する。

## タグ別ログ
指定期間の日付の若い順番から列挙する。
### タグ件数
件数を多い順に一覧表にする。
"""


@pytest.fixture
def daily_path(tmp_path: Path) -> Path:
    directory = tmp_path / "01_Daily"
    directory.mkdir()
    (directory / "2026-08-05.md").write_text(DAILY_0805, encoding="utf-8")
    (directory / "2026-08-07.md").write_text(DAILY_0807, encoding="utf-8")
    return directory


@pytest.fixture
def templates_path(tmp_path: Path) -> Path:
    directory = tmp_path / "00_Templates"
    directory.mkdir()
    (directory / TEMPLATE_FILENAME).write_text(TEMPLATE, encoding="utf-8")
    return directory


@pytest.fixture
def summary_path(tmp_path: Path) -> Path:
    return tmp_path / "11_Summary"
