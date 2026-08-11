"""UI表示メッセージと日誌フォーマットの定数。"""

APP_TITLE = "WorkScribe 業務日誌まとめ"

LABEL_START_DATE = "開始日"
LABEL_END_DATE = "終了日"
BUTTON_CREATE = "まとめを作成"

CONFIRM_OVERWRITE = "{name} は既に存在します。上書きしますか？"
SUCCESS_CREATED = "業務日誌まとめを作成しました。\n\n{path}"

ERROR_INVALID_RANGE = "開始日は終了日より前の日付を指定してください。"
ERROR_NO_DAILY_FILES = "指定した期間に日誌ファイルがありません。"
ERROR_TEMPLATE_NOT_FOUND = "テンプレートが見つかりません。\n\n{path}"
ERROR_DAILY_DIR_NOT_FOUND = "日誌フォルダが見つかりません。\n\n{path}"
ERROR_UNEXPECTED = "処理中にエラーが発生しました。\n\n{detail}"

TEMPLATE_FILENAME = "業務日誌まとめテンプレート.md"
DAILY_DATE_FORMAT = "%Y-%m-%d"
SUMMARY_DATE_FORMAT = "%Y%m%d"

SECTION_DAILY_LOG = "本日のログ"
SECTION_SUCCESSES = "うまくいったこと"
SECTION_ISSUES = "課題と対策"
SECTION_LEARNINGS = "学びと気づき"
SECTION_TAG_LOG = "タグ別ログ"
SUBSECTION_TAG_COUNT = "タグ件数"

TARGET_TAGS = ("#移譲", "#説明", "#評価", "#対人", "#開発", "#トラブル")

TAG_COUNT_TABLE_HEADER = "| カテゴリ | 件数 |\n| --- | --- |"
NO_ITEMS_TEXT = "（該当なし）"

PLACEHOLDER_TITLE = "{{title}}"
PLACEHOLDER_START_DATE = "{開始日(yyyymmdd形式)}"
PLACEHOLDER_END_DATE = "{終了日(yyyymmdd形式)}"
