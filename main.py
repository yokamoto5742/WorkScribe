from app.main_window import MainWindow
from utils.log_rotation import setup_logging


def main() -> None:
    setup_logging()
    MainWindow().mainloop()


if __name__ == "__main__":
    main()
