from typing import Optional
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton,
    QLabel, QHBoxLayout, QLineEdit
)


class ItemList(QWidget):
    sigItemSelected = pyqtSignal(int)
    sigClearRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._list = QListWidget(self)

        lbl = QLabel("Список объектов")
        self.le_search = QLineEdit(self)
        self.le_search.setPlaceholderText("Поиск по названию...")
        btn_clear_all = QPushButton("Очистить всё")

        top_bar = QHBoxLayout()
        top_bar.addWidget(lbl)
        top_bar.addStretch(1)
        top_bar.addWidget(btn_clear_all)

        layout = QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(self.le_search)
        layout.addWidget(self._list)

        self._list.currentItemChanged.connect(self._on_current_changed)
        btn_clear_all.clicked.connect(self.sigClearRequested.emit)
        self.le_search.textChanged.connect(self._apply_filter)

        self._id_by_row: list[int] = []
        self._all_items: list[dict] = []

    def refresh(self, items: list[dict], filter_text: str = ""):
        self._all_items = items
        self._apply_filter(filter_text)

    def _apply_filter(self, text: str = ""):
        text = text.strip().lower()
        self._list.clear()
        self._id_by_row.clear()

        for obj in self._all_items:
            title = obj.get("title", "")
            if not text or text in title.lower():
                item = QListWidgetItem(title or "(без названия)")
                self._list.addItem(item)
                self._id_by_row.append(obj["id"])

    def current_filter(self) -> str:
        return self.le_search.text().strip()

    def current_item_id(self) -> Optional[int]:
        row = self._list.currentRow()
        if row < 0 or row >= len(self._id_by_row):
            return None
        return self._id_by_row[row]

    @pyqtSlot()
    def _on_current_changed(self):
        item_id = self.current_item_id()
        if item_id is not None:
            self.sigItemSelected.emit(item_id)