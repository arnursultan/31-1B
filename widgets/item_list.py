from typing import Optional
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton,
    QLabel, QHBoxLayout, QLineEdit
)

class ItemList(QWidget):
    # Сигнал, когда выбран элемент (отправляем его id)
    sigItemSelected = pyqtSignal(int)
    # Сигнал, когда пользователь хочет очистить всё хранилище
    sigClearRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Виджет списка
        self._list = QListWidget(self)

        # Надпись сверху и поле для поиска
        lbl = QLabel("Список объектов")
        self.le_search = QLineEdit(self)
        self.le_search.setPlaceholderText("Поиск по названию...")

        # Кнопка очистки всего списка/хранилища
        btn_clear_all = QPushButton("Очистить всё")

        # Горизонтальный лэйаут для заголовка и кнопки
        top_bar = QHBoxLayout()
        top_bar.addWidget(lbl)
        top_bar.addStretch(1)          # чтобы кнопка была справа
        top_bar.addWidget(btn_clear_all)

        # Основной вертикальный лэйаут
        layout = QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(self.le_search)  # поле поиска под заголовком
        layout.addWidget(self._list)      # список объектов

        # Сигналы
        self._list.currentItemChanged.connect(self._on_current_changed)  # когда меняем выбор
        btn_clear_all.clicked.connect(self.sigClearRequested.emit)       # клик на очистку
        self.le_search.textChanged.connect(self._apply_filter)           # поиск по тексту

        # Для сопоставления строк списка с id элементов
        self._id_by_row: list[int] = []
        # Храним все элементы для фильтрации
        self._all_items: list[dict] = []

    def refresh(self, items: list[dict], filter_text: str = ""):
        # Обновляем список всех элементов и применяем фильтр
        self._all_items = items
        self._apply_filter(filter_text)

    def _apply_filter(self, text: str = ""):
        # Фильтруем список по тексту поиска
        text = text.strip().lower()  # делаем поиск нечувствительным к регистру
        self._list.clear()
        self._id_by_row.clear()

        for obj in self._all_items:
            title = obj.get("title", "")
            if not text or text in title.lower():  # если текст пустой или совпадение есть
                item = QListWidgetItem(title or "(без названия)")
                self._list.addItem(item)
                self._id_by_row.append(obj["id"])  # сохраняем id, чтобы потом знать, какой выбран

    def current_filter(self) -> str:
        # Возвращаем текст из поля поиска
        return self.le_search.text().strip()

    def current_item_id(self) -> Optional[int]:
        # Возвращаем id текущего выбранного элемента
        row = self._list.currentRow()
        if row < 0 or row >= len(self._id_by_row):
            return None
        return self._id_by_row[row]

    @pyqtSlot()
    def _on_current_changed(self):
        # Когда меняется выбранный элемент — отправляем его id
        item_id = self.current_item_id()
        if item_id is not None:
            self.sigItemSelected.emit(item_id)
