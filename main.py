import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PyQt6 проект")

    window = MainWindow()
    window.resize(900, 600)
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()