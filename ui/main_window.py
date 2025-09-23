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

        # Хранилище данных (пока в памяти, позже можно подключить БД)
        self.storage = InMemoryStorage()

        # Виджеты интерфейса
        self.item_list = ItemList()  # список элементов
        self.item_form = ItemForm()  # форма редактирования/создания

        # Центральный виджет и лэйаут
        central = QWidget(self)
        layout = QHBoxLayout(central)
        # stretch определяет относительную ширину виджетов:
        # item_list занимает 2 части, item_form — 3 части ширины
        layout.addWidget(self.item_list, stretch=2)
        layout.addWidget(self.item_form, stretch=3)
        self.setCentralWidget(central)

        # Статус-бар для сообщений пользователю
        self._init_statusbar()

        # Тулбар с кнопками
        self._init_toolbar()

        # Подключаем сигналы (слоты — методы, которые реагируют на события)
        self._connect_signals()

        # Загружаем демо-элементы, чтобы не было пустого списка
        self._bootstrap_demo_items()

    def _init_statusbar(self):
        # Создаём статус-бар и выводим начальное сообщение
        status = QStatusBar(self)
        self.setStatusBar(status)
        self.statusBar().showMessage("Готово")

    def _init_toolbar(self):
        # Создаём тулбар и добавляем кнопки
        toolbar = QToolBar("Основные действия", self)
        self.addToolBar(toolbar)

        # Кнопка "Добавить"
        act_add = QAction("Добавить", self)
        act_add.triggered.connect(self.on_add_clicked)  # связываем сигнал clicked с методом
        toolbar.addAction(act_add)

        # Кнопка "Очистить форму"
        act_clear = QAction("Очистить форму", self)
        act_clear.triggered.connect(self.item_form.clear_form)
        toolbar.addAction(act_clear)

        # Кнопка "Удалить выбранный" с горячей клавишей Delete
        act_delete = QAction("Удалить выбранный", self)
        act_delete.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        act_delete.triggered.connect(self.on_delete_selected)
        toolbar.addAction(act_delete)

        # Кнопка "Дублировать"
        act_duplicate = QAction("Дублировать", self)
        act_duplicate.triggered.connect(self.on_duplicate_selected)
        toolbar.addAction(act_duplicate)

        # Кнопка "О программе"
        act_about = QAction("О программе", self)
        act_about.triggered.connect(self.on_about)
        toolbar.addAction(act_about)

        # Кнопка "Сохранить" с Ctrl+S (добавляем на окно, чтобы работала горячая клавиша)
        act_save = QAction("Сохранить", self)
        act_save.setShortcut(QKeySequence.StandardKey.Save)
        act_save.triggered.connect(self.item_form._emit_save)
        self.addAction(act_save)

    def _connect_signals(self):
        """
        Связываем сигналы виджетов с методами окна:
        - sigItemSelected — пользователь выбрал элемент в списке
        - sigSaveRequested — форма запросила сохранение данных
        - sigClearRequested — очистка всего хранилища
        """
        self.item_list.sigItemSelected.connect(self.on_item_selected)
        self.item_form.sigSaveRequested.connect(self.on_save_requested)
        self.item_list.sigClearRequested.connect(self.on_clear_storage)

    def _bootstrap_demo_items(self):
        # Несколько демонстрационных элементов, чтобы сразу было что показывать
        demo = [
            {"title": "Ubuntu", "description": "Дистрибутив Linux", "tags": "linux, os"},
            {"title": "PyQt6", "description": "Фреймворк для GUI на Python", "tags": "python, gui"},
        ]
        for d in demo:
            self.storage.create(d)
        # Обновляем список после загрузки демо-данных
        self.item_list.refresh(self.storage.list_all())

    @pyqtSlot(dict)
    def on_save_requested(self, data: dict):
        # Слот: вызывается при сохранении элемента из формы
        title = (data.get("title") or "").strip()
        if not title:
            QMessageBox.warning(self, "Ошибка валидации", "Поле 'Название' обязательно!")
            return

        item_id = data.get("id")
        if item_id:
            # Если есть id — обновляем элемент
            updated = self.storage.update(item_id, data)
            self.statusBar().showMessage(f"Обновлено: {updated['title']}")
        else:
            # Если id нет — создаём новый элемент
            created = self.storage.create(data)
            self.statusBar().showMessage(f"Создано: {created['title']}")

        # Обновляем список с учётом фильтра (если пользователь использует поиск)
        self.item_list.refresh(self.storage.list_all(), self.item_list.current_filter())
        # Очищаем форму после сохранения
        self.item_form.clear_form()

    @pyqtSlot(int)
    def on_item_selected(self, item_id: int):
        # Пользователь выбрал элемент в списке
        obj = self.storage.get(item_id)
        if obj:
            # Заполняем форму выбранным элементом
            self.item_form.fill_form(obj)

    @pyqtSlot()
    def on_add_clicked(self):
        # Добавление элемента через кнопку "Добавить"
        data = self.item_form.collect_data()
        title = (data.get("title") or "").strip()
        if not title:
            QMessageBox.warning(self, "Ошибка валидации", "Поле 'Название' обязательно!")
            return

        created = self.storage.create(data)
        # Обновляем список с текущим фильтром
        self.item_list.refresh(self.storage.list_all(), self.item_list.current_filter())
        self.item_form.clear_form()
        self.statusBar().showMessage(f"Создано: {created['title']}")

    @pyqtSlot()
    def on_delete_selected(self):
        # Удаляем выбранный элемент
        item_id = self.item_list.current_item_id()
        if item_id is None:
            QMessageBox.information(self, "Удаление", "Не выбран элемент.")
            return
        self.storage.delete(item_id)
        # Обновляем список с текущим фильтром и очищаем форму
        self.item_list.refresh(self.storage.list_all(), self.item_list.current_filter())
        self.item_form.clear_form()
        self.statusBar().showMessage("Удалено")

    @pyqtSlot()
    def on_duplicate_selected(self):
        # Дублируем выбранный элемент
        item_id = self.item_list.current_item_id()
        if item_id is None:
            QMessageBox.information(self, "Дублирование", "Не выбран элемент.")
            return
        obj = self.storage.get(item_id)
        if obj:
            new_data = obj.copy()
            new_data["id"] = None  # сбрасываем id, чтобы создать новый элемент
            created = self.storage.create(new_data)
            # Обновляем список с текущим фильтром
            self.item_list.refresh(self.storage.list_all(), self.item_list.current_filter())
            self.statusBar().showMessage(f"Скопировано: {created['title']}")

    @pyqtSlot()
    def on_clear_storage(self):
        # Полностью очищаем хранилище
        self.storage.clear()
        # Обновляем виджеты после очистки
        self.item_list.refresh(self.storage.list_all())
        self.item_form.clear_form()
        self.statusBar().showMessage("Хранилище очищено")

    @pyqtSlot()
    def on_about(self):
        # Окно "О программе" с краткой информацией
        QMessageBox.information(
            self, "О программе",
            "PyQt6 CRUD:\n"
            "— Валидация title\n"
            "— Поиск в поиске (фильтр)\n"
            "— Дублирование элементов\n"
            "— Горячие клавиши для удобства"
        )
