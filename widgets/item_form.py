from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QLabel
)

class ItemForm(QWidget):
    sigSaveRequested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._id: int | None = None

        self.le_title = QLineEdit(self)
        self.te_description = QTextEdit(self)
        self.le_tags = QLineEdit(self)

        form = QFormLayout()
        form.addRow("Название *", self.le_title)
        form.addRow("Описание", self.te_description)
        form.addRow("Теги", self.le_tags)

        self.btn_save = QPushButton("Сохранить")
        self.btn_clear = QPushButton("Очистить")

        btns = QHBoxLayout()
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_clear)
        btns.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Форма объекта"))
        layout.addLayout(form)
        layout.addLayout(btns)
        layout.addStretch(1)

        self.btn_save.clicked.connect(self._emit_save)
        self.btn_clear.clicked.connect(self.clear_form)

    def collect_data(self) -> dict:
        return {
            "id": self._id,
            "title": self.le_title.text().strip(),
            "description": self.te_description.toPlainText().strip(),
            "tags": self.le_tags.text().strip(),
        }

    def fill_form(self, obj: dict):
        self._id = obj.get("id")
        self.le_title.setText(obj.get("title", ""))
        self.te_description.setPlainText(obj.get("description", ""))
        self.le_tags.setText(obj.get("tags", ""))

    def clear_form(self):
        self._id = None
        self.le_title.clear()
        self.te_description.clear()
        self.le_tags.clear()

    def _emit_save(self):
        self.sigSaveRequested.emit(self.collect_data())
