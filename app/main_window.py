"""日付を指定して業務日誌まとめ・1週間の振り返りを作成するメイン画面。"""

import logging
import tkinter as tk
from datetime import date, timedelta
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable

from tkcalendar import DateEntry

from app.constants import (
    APP_TITLE,
    BUTTON_CREATE,
    BUTTON_CREATE_REVIEW,
    CONFIRM_OVERWRITE,
    ERROR_INVALID_RANGE,
    ERROR_UNEXPECTED,
    LABEL_END_DATE,
    LABEL_START_DATE,
    SUCCESS_CREATED,
    SUCCESS_REVIEW_CREATED,
)
from service.weekly_review import create_weekly_review, review_file_path
from service.weekly_summary import WeeklySummaryError, create_weekly_summary, summary_file_path
from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

DEFAULT_PERIOD_DAYS = 6
DEFAULT_WINDOW_WIDTH = 360
DEFAULT_WINDOW_HEIGHT = 220


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self._config_manager = ConfigManager()
        width = self._config_manager.get_int("UI", "window_width", DEFAULT_WINDOW_WIDTH)
        height = self._config_manager.get_int("UI", "window_height", DEFAULT_WINDOW_HEIGHT)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self._start_entry, self._end_entry = self._build_widgets()

    def _build_widgets(self) -> tuple[DateEntry, DateEntry]:
        # ウィンドウサイズに追従させ、config.ini の設定を反映させる
        self.columnconfigure(0, weight=1)
        frame = ttk.Frame(self, padding=16)
        frame.grid(row=0, column=0, sticky=tk.EW)
        frame.columnconfigure(1, weight=1)

        today = date.today()
        start_entry = self._add_date_row(frame, 0, LABEL_START_DATE, today - timedelta(days=DEFAULT_PERIOD_DAYS))
        end_entry = self._add_date_row(frame, 1, LABEL_END_DATE, today)

        self._add_button(frame, 2, BUTTON_CREATE, self._on_create, top_padding=16)
        self._add_button(frame, 3, BUTTON_CREATE_REVIEW, self._on_create_review, top_padding=8)
        return start_entry, end_entry

    @staticmethod
    def _add_date_row(frame: ttk.Frame, row: int, label: str, initial: date) -> DateEntry:
        ttk.Label(frame, text=label).grid(row=row, column=0, padx=(0, 8), pady=4, sticky=tk.W)
        entry = DateEntry(frame, width=12, date_pattern="yyyy-mm-dd", year=initial.year,
                          month=initial.month, day=initial.day)
        entry.grid(row=row, column=1, pady=4, sticky=tk.W)
        return entry

    @staticmethod
    def _add_button(frame: ttk.Frame, row: int, text: str, command: Callable[[], None],
                    top_padding: int) -> None:
        button = ttk.Button(frame, text=text, command=command)
        button.grid(row=row, column=0, columnspan=2, pady=(top_padding, 0), sticky=tk.EW)

    def _on_create(self) -> None:
        self._create(self._create_summary, SUCCESS_CREATED)

    def _on_create_review(self) -> None:
        self._create(self._create_review, SUCCESS_REVIEW_CREATED)

    def _create(self, create_file: Callable[[date, date], Path | None], success_message: str) -> None:
        start: date = self._start_entry.get_date()
        end: date = self._end_entry.get_date()
        if start > end:
            messagebox.showerror(APP_TITLE, ERROR_INVALID_RANGE)
            return

        try:
            output_path = create_file(start, end)
        except WeeklySummaryError as e:
            messagebox.showerror(APP_TITLE, str(e))
            return
        except (OSError, ValueError) as e:
            logger.exception("ファイルの作成に失敗しました")
            messagebox.showerror(APP_TITLE, ERROR_UNEXPECTED.format(detail=e))
            return

        if output_path is not None:
            messagebox.showinfo(APP_TITLE, success_message.format(path=output_path))

    def _create_summary(self, start: date, end: date) -> Path | None:
        summary_path = self._config_manager.get_path("summary_path")
        if not self._confirm_overwrite(summary_file_path(summary_path, start, end)):
            return None

        created_path = create_weekly_summary(
            templates_path=self._config_manager.get_path("templates_path"),
            daily_path=self._config_manager.get_path("daily_path"),
            summary_path=summary_path,
            start=start,
            end=end,
        )
        logger.info(f"業務日誌まとめを作成しました: {created_path}")
        return created_path

    def _create_review(self, start: date, end: date) -> Path | None:
        weekly_path = self._config_manager.get_path("weekly_path")
        if not self._confirm_overwrite(review_file_path(weekly_path, start, end)):
            return None

        created_path = create_weekly_review(
            templates_path=self._config_manager.get_path("templates_path"),
            weekly_path=weekly_path,
            start=start,
            end=end,
        )
        logger.info(f"1週間の振り返りを作成しました: {created_path}")
        return created_path

    @staticmethod
    def _confirm_overwrite(output_path: Path) -> bool:
        if not output_path.exists():
            return True
        return messagebox.askyesno(APP_TITLE, CONFIRM_OVERWRITE.format(name=output_path.name))
