"""日付を指定して業務日誌まとめを作成するメイン画面。"""

import logging
import tkinter as tk
from datetime import date, timedelta
from pathlib import Path
from tkinter import messagebox, ttk

from tkcalendar import DateEntry

from app.constants import (
    APP_TITLE,
    BUTTON_CREATE,
    CONFIRM_OVERWRITE,
    ERROR_INVALID_RANGE,
    ERROR_UNEXPECTED,
    LABEL_END_DATE,
    LABEL_START_DATE,
    SUCCESS_CREATED,
)
from service.weekly_summary import WeeklySummaryError, create_weekly_summary, summary_file_path
from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

DEFAULT_PERIOD_DAYS = 6


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.resizable(False, False)
        self._config_manager = ConfigManager()
        self._start_entry, self._end_entry = self._build_widgets()

    def _build_widgets(self) -> tuple[DateEntry, DateEntry]:
        frame = ttk.Frame(self, padding=16)
        frame.grid(row=0, column=0)

        today = date.today()
        start_entry = self._add_date_row(frame, 0, LABEL_START_DATE, today - timedelta(days=DEFAULT_PERIOD_DAYS))
        end_entry = self._add_date_row(frame, 1, LABEL_END_DATE, today)

        button = ttk.Button(frame, text=BUTTON_CREATE, command=self._on_create)
        button.grid(row=2, column=0, columnspan=2, pady=(16, 0), sticky=tk.EW)
        return start_entry, end_entry

    @staticmethod
    def _add_date_row(frame: ttk.Frame, row: int, label: str, initial: date) -> DateEntry:
        ttk.Label(frame, text=label).grid(row=row, column=0, padx=(0, 8), pady=4, sticky=tk.W)
        entry = DateEntry(frame, width=12, date_pattern="yyyy-mm-dd", year=initial.year,
                          month=initial.month, day=initial.day)
        entry.grid(row=row, column=1, pady=4, sticky=tk.W)
        return entry

    def _on_create(self) -> None:
        start: date = self._start_entry.get_date()
        end: date = self._end_entry.get_date()
        if start > end:
            messagebox.showerror(APP_TITLE, ERROR_INVALID_RANGE)
            return

        try:
            output_path = self._create_summary(start, end)
        except WeeklySummaryError as e:
            messagebox.showerror(APP_TITLE, str(e))
            return
        except (OSError, ValueError) as e:
            logger.exception("業務日誌まとめの作成に失敗しました")
            messagebox.showerror(APP_TITLE, ERROR_UNEXPECTED.format(detail=e))
            return

        if output_path is not None:
            messagebox.showinfo(APP_TITLE, SUCCESS_CREATED.format(path=output_path))

    def _create_summary(self, start: date, end: date) -> Path | None:
        summary_path = self._config_manager.get_path("summary_path")
        output_path = summary_file_path(summary_path, start, end)
        if output_path.exists():
            if not messagebox.askyesno(APP_TITLE, CONFIRM_OVERWRITE.format(name=output_path.name)):
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
