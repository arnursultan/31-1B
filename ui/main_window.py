from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStatusBar, QToolBar, QMessageBox
)
from widgets.item_list import ItemList
from widgets.item_form import ItemForm
from models.storage import InMemoryStorage


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PyQt6 CRUD — каркас")

        self.storage = InMemoryStorage()

        self.item_list = ItemList()
        self.item_form = ItemForm()

        central = QWidget(self)
        layout = QHBoxLayout(central)
        layout.addWidget(self.item_list, stretch=2)
        layout.addWidget(self.item_form, stretch=3)
        self.setCentralWidget(central)

        self._init_statusbar()
        self._init_toolbar()

        self._connect_signals()

        self._bootstrap_demo_items()

    def _init_statusbar(self):
        status = QStatusBar(self)
        self.setStatusBar(status)
        self.statusBar().showMessage("Готово")

    def _init_toolbar(self):
        toolbar = QToolBar("Основные действия", self)
        self.addToolBar(toolbar)

        act_add = QAction("Добавить", self)
        act_add.triggered.connect(self.on_add_clicked)
        toolbar.addAction(act_add)

        act_clear = QAction("Очистить форму", self)
        act_clear.triggered.connect(self.item_form.clear_form)
        toolbar.addAction(act_clear)

        act_delete = QAction("Удалить выбранный", self)
        act_delete.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        act_delete.triggered.connect(self.on_delete_selected)
        toolbar.addAction(act_delete)

        act_duplicate = QAction("Дублировать", self)
        act_duplicate.triggered.connect(self.on_duplicate_selected)
        toolbar.addAction(act_duplicate)

        act_about = QAction("О программе", self)
        act_about.triggered.connect(self.on_about)
        toolbar.addAction(act_about)

        act_save = QAction("Сохранить", self)
        act_save.setShortcut(QKeySequence.StandardKey.Save)  # Ctrl+S
        act_save.triggered.connect(self.item_form._emit_save)
        self.addAction(act_save)

    def _connect_signals(self):
        self.item_list.sigItemSelected.connect(self.on_item_selected)
        self.item_form.sigSaveRequested.connect(self.on_save_requested)
        self.item_list.sigClearRequested.connect(self.on_clear_storage)

    def _bootstrap_demo_items(self):
        demo = [
            {"title": "Ubuntu", "description": "Дистрибутив Linux", "tags": "linux, os"},
            {"title": "PyQt6", "description": "Фреймворк для GUI на Python", "tags": "python, gui"},
        ]
        for d in demo:
            self.storage.create(d)
        self.item_list.refresh(self.storage.list_all())

    @pyqtSlot(dict)
    def on_save_requested(self, data: dict):
        title = (data.get("title") or "").strip()
        if not title:
            QMessageBox.warning(self, "Ошибка валидации", "Поле 'Название' обязательно!")
            return

        item_id = data.get("id")
        if item_id:
            updated = self.storage.update(item_id, data)
            self.statusBar().showMessage(f"Обновлено: {updated['title']}")
        else:
            created = self.storage.create(data)
            self.statusBar().showMessage(f"Создано: {created['title']}")

        self.item_list.refresh(self.storage.list_all(), self.item_list.current_filter())
        self.item_form.clear_form()

    @pyqtSlot(int)
    def on_item_selected(self, item_id: int):
        obj = self.storage.get(item_id)
        if obj:
            self.item_form.fill_form(obj)

    @pyqtSlot()
    def on_add_clicked(self):
        data = self.item_form.collect_data()
        title = (data.get("title") or "").strip()
        if not title:
            QMessageBox.warning(self, "Ошибка валидации", "Поле 'Название' обязательно!")
            return

        created = self.storage.create(data)
        self.item_list.refresh(self.storage.list_all(), self.item_list.current_filter())
        self.item_form.clear_form()
        self.statusBar().showMessage(f"Создано: {created['title']}")

    @pyqtSlot()
    def on_delete_selected(self):
        item_id = self.item_list.current_item_id()
        if item_id is None:
            QMessageBox.information(self, "Удаление", "Не выбран элемент.")
            return
        self.storage.delete(item_id)
        self.item_list.refresh(self.storage.list_all(), self.item_list.current_filter())
        self.item_form.clear_form()
        self.statusBar().showMessage("Удалено")

    @pyqtSlot()
    def on_duplicate_selected(self):
        item_id = self.item_list.current_item_id()
        if item_id is None:
            QMessageBox.information(self, "Дублирование", "Не выбран элемент.")
            return
        obj = self.storage.get(item_id)
        if obj:
            new_data = obj.copy()
            new_data["id"] = None  # сбрасываем id
            created = self.storage.create(new_data)
            self.item_list.refresh(self.storage.list_all(), self.item_list.current_filter())
            self.statusBar().showMessage(f"Скопировано: {created['title']}")

    @pyqtSlot()
    def on_clear_storage(self):
        self.storage.clear()
        self.item_list.refresh(self.storage.list_all())
        self.item_form.clear_form()
        self.statusBar().showMessage("Хранилище очищено")

    @pyqtSlot()
    def on_about(self):
        QMessageBox.information(
            self, "О программе",
            "PyQt6 CRUD:\n"
            "— Валидация title\n"
            "— Поиск в поиске\n"
            "— Дублирование\n"
            "— Горячие клавиши"
        )
