"""
人事評価Excelファイル → Wordドキュメント変換スクリプト

使用方法:
    # 単一ファイル
    python excel_to_word_hr_evaluation.py A03人事評価　一般職3等級.xlsx

    # 複数ファイル
    python excel_to_word_hr_evaluation.py A02人事評価_一般職2等級.xlsx A03人事評価_一般職3等級.xlsx

    # ワイルドカード
    python excel_to_word_hr_evaluation.py A0*.xlsx

    # 出力先ディレクトリ指定
    python excel_to_word_hr_evaluation.py A02人事評価_一般職2等級.xlsx --output-dir ./出力

Excelファイルの列構造:
    B列: 被評価者名
    H列: No.1 評価を選んだ理由（被評価者記載）
    K列: No.2 評価を選んだ理由（被評価者記載）
    M列: 振り返り
    データ行: 5行目以降

必要ライブラリ:
    pip install openpyxl python-docx
"""

import argparse
import glob
import io
import sys
import zipfile
from pathlib import Path

import openpyxl
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

# ─── 列インデックス（1始まり） ───────────────────────────
COL_NAME = 2        # B列: 被評価者名
COL_NO1 = 8         # H列: No.1 評価理由
COL_NO2 = 11        # K列: No.2 評価理由
COL_FURIKAERI = 13  # M列: 振り返り
DATA_START_ROW = 5  # データ開始行

FONT_JP = "MS Mincho"
FONT_SIZE_BODY = Pt(11)
FONT_SIZE_NAME = Pt(12)


# ─── ドキュメント構築ヘルパー ────────────────────────────

def _set_east_asia_font(run, font_name: str) -> None:
    """TextRun に日本語フォント（eastAsia）を設定する"""
    rpr = run._r.get_or_add_rPr()
    existing = rpr.find(qn("w:rFonts"))
    if existing is not None:
        existing.set(qn("w:eastAsia"), font_name)
    else:
        rfonts = OxmlElement("w:rFonts")
        rfonts.set(qn("w:eastAsia"), font_name)
        rpr.insert(0, rfonts)


def _apply_run(run, bold: bool = False, size: Pt = FONT_SIZE_BODY) -> None:
    """TextRun にフォント・サイズ・太字を適用する"""
    run.font.name = FONT_JP
    run.font.size = size
    run.font.bold = bold
    _set_east_asia_font(run, FONT_JP)


def _set_para_spacing(
    para, before: int = 0, after: int = 0, line: int = 360
) -> None:
    """段落の行間・段落前後スペースを設定する（twips単位）"""
    ppr = para._p.get_or_add_pPr()
    existing = ppr.find(qn("w:spacing"))
    if existing is not None:
        ppr.remove(existing)
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:before"), str(before))
    spacing.set(qn("w:after"), str(after))
    spacing.set(qn("w:line"), str(line))
    spacing.set(qn("w:lineRule"), "auto")
    ppr.append(spacing)


def add_label(doc: Document, text: str) -> None:
    """ラベル段落（No.1 / 評価を選んだ理由 / 振り返り 等）を追加する"""
    para = doc.add_paragraph()
    run = para.add_run(text)
    _apply_run(run, bold=True)
    _set_para_spacing(para, before=100, after=40)


def add_text_block(doc: Document, text: str) -> None:
    """改行を含む本文テキストを段落として追加する"""
    if not text:
        return
    for line in str(text).splitlines():
        para = doc.add_paragraph()
        run = para.add_run(line)
        _apply_run(run)
        _set_para_spacing(para, line=360)


def add_person(
    doc: Document, name: str, no1: str, no2: str, furikaeri: str
) -> None:
    """1名分のセクションをドキュメントに追加する"""
    # 被評価者名
    para = doc.add_paragraph()
    run = para.add_run(f"被評価者名\u3000{name}")
    _apply_run(run, bold=True, size=FONT_SIZE_NAME)
    _set_para_spacing(para, after=150)

    # No.1
    add_label(doc, "No.1")
    add_label(doc, "評価を選んだ理由（被評価者記載）")
    add_text_block(doc, no1)

    # No.2
    add_label(doc, "No.2")
    add_label(doc, "評価を選んだ理由（被評価者記載）")
    add_text_block(doc, no2)

    # 振り返り
    add_label(doc, "振り返り")
    add_text_block(doc, furikaeri)


def set_page_margins(doc: Document) -> None:
    """A4・余白設定"""
    for section in doc.sections:
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)


# ─── settings.xml 修正 ──────────────────────────────────

def fix_zoom_settings(path: Path) -> None:
    """python-docx が生成する settings.xml の w:zoom 属性不足を修正する。

    python-docx は <w:zoom w:val="bestFit"/> を出力するが、
    OOXML スキーマでは w:percent 属性が必須のため、バリデーションエラーになる。
    保存後に ZIP を開き直して settings.xml を書き換える。
    """
    with zipfile.ZipFile(path, "r") as zin:
        names = zin.namelist()
        entries = {name: zin.read(name) for name in names}

    target = "word/settings.xml"
    if target in entries:
        xml = entries[target].decode("utf-8")
        xml = xml.replace(
            '<w:zoom w:val="bestFit"/>',
            '<w:zoom w:val="bestFit" w:percent="100"/>',
        )
        entries[target] = xml.encode("utf-8")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            zout.writestr(name, entries[name])
    path.write_bytes(buf.getvalue())


# ─── Excel 読み込み ──────────────────────────────────────

def read_excel(path: Path) -> list[dict]:
    """Excelファイルを読み込み、被評価者データのリストを返す"""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    persons = []
    for row in ws.iter_rows(min_row=DATA_START_ROW):
        name = row[COL_NAME - 1].value
        if not name or str(name).strip() == "":
            continue
        persons.append({
            "name": str(name).strip(),
            "no1": str(row[COL_NO1 - 1].value or "").strip(),
            "no2": str(row[COL_NO2 - 1].value or "").strip(),
            "furikaeri": str(row[COL_FURIKAERI - 1].value or "").strip(),
        })
    return persons


# ─── 変換メイン ──────────────────────────────────────────

def build_output_path(input_path: Path, output_dir: Path) -> Path:
    """出力Wordファイルのパスを生成する（例: 評価コメントA02人事評価_一般職2等級.docx）"""
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"評価コメント{input_path.stem}.docx"


def convert(input_path: Path, output_dir: Path) -> Path:
    """ExcelファイルをWordドキュメントに変換して保存し、出力パスを返す"""
    persons = read_excel(input_path)
    if not persons:
        raise ValueError(f"データが見つかりません: {input_path}")

    doc = Document()
    set_page_margins(doc)
    doc.styles["Normal"].font.name = FONT_JP
    doc.styles["Normal"].font.size = FONT_SIZE_BODY

    for i, person in enumerate(persons):
        if i > 0:
            doc.add_page_break()
        add_person(doc, **person)

    output_path = build_output_path(input_path, output_dir)
    doc.save(output_path)
    fix_zoom_settings(output_path)
    return output_path


# ─── CLI ─────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="人事評価Excelファイル → Wordドキュメント変換"
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="変換するExcelファイル（ワイルドカード可）",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="出力先ディレクトリ（デフォルト: カレントディレクトリ）",
    )
    args = parser.parse_args()

    # ワイルドカードを展開
    input_paths: list[Path] = []
    for pattern in args.inputs:
        matched = glob.glob(pattern)
        if matched:
            input_paths.extend(Path(p) for p in matched)
        else:
            input_paths.append(Path(pattern))

    output_dir = Path(args.output_dir)
    errors: list[Path] = []

    for input_path in input_paths:
        if not input_path.exists():
            print(f"[スキップ] ファイルが見つかりません: {input_path}", file=sys.stderr)
            errors.append(input_path)
            continue
        try:
            output_path = convert(input_path, output_dir)
            print(f"[完了] {input_path.name} → {output_path}")
        except Exception as e:
            print(f"[エラー] {input_path.name}: {e}", file=sys.stderr)
            errors.append(input_path)

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
