# CLAUDE.md

このファイルは、このリポジトリで作業する際にClaude Code (claude.ai/code) に向けたガイダンスを提供します。

## プロジェクト概要

WorkScribeは、業務日誌データを処理するTkinter製デスクトップGUIアプリケーション（Windows向け）です。日次・週次の業務日誌を要約し、Excel形式の人事評価をWord文書に変換します。エントリーポイントは`main.py`で、`MainWindow`（`app/main_window.py`）を起動します。

## アーキテクチャ

- `app/` — TkinterのGUI（`main_window.py`、UIメッセージ定数用の`constants.py`）
- `service/` — 業務ロジック（`daily_parser.py`、`weekly_summary.py`）
- `utils/` — `config_manager.py`が`config.ini`を読み込む。`log_rotation.py`はログ管理用
- `scripts/` — 単体スクリプト群（例: `excel_to_word_hr_evaluation.py`）
- `tests/` — `service/`に対応したpytestスイート（例: `tests/service/test_daily_parser.py`）
- `build.py` — `utils/config.ini`を同梱し、ウィンドウ型.exeを生成するPyInstallerパッケージングスクリプト

設定はすべて`utils/config.ini`によるファイルベースで管理されており、環境変数は使用しません。`[Path]`セクションにはテンプレート・日次・週次・サマリーの各フォルダパス、`[LOGGING]`セクションにはログ保持日数・保存先・ログレベル・デバッグ設定が定義されています。

## 環境とコマンド

このプロジェクトは`uv`を使用します（`uv.lock`、`pyproject.toml`を参照。Python >=3.13が必要）。

```bash
uv sync              # 依存関係のインストール
uv run main.py        # アプリの実行
uv run build.py       # PyInstallerによるWindows向け.exeのパッケージング
```

型チェック: `pyright`（`pyproject.toml`で設定、standardモード。`app/`、`service/`、`utils/`、`tests/`が対象）。

## ルール

追加の指示は`.claude/rules/`にあります: `coding-guidelines.md`、`python-coding.md`、`response-style.md`、`testing.md`。これらは自動的に読み込まれます。
