from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QLabel
)

class ItemForm(QWidget):
    # Сигнал, который будет отправляться при сохранении элемента
    sigSaveRequested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Сюда сохраняем id текущего редактируемого элемента, None если новый
        self._id: int | None = None

        # Поля формы
        self.le_title = QLineEdit(self)          # название
        self.te_description = QTextEdit(self)    # описание
        self.le_tags = QLineEdit(self)           # теги

        # Форм-лейаут для подписей и полей
        form = QFormLayout()
        form.addRow("Название *", self.le_title)
        form.addRow("Описание", self.te_description)
        form.addRow("Теги", self.le_tags)

        # Кнопки сохранения и очистки формы
        self.btn_save = QPushButton("Сохранить")
        self.btn_clear = QPushButton("Очистить")

        # Горизонтальный лэйаут для кнопок
        btns = QHBoxLayout()
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_clear)
        btns.addStretch(1)  # чтобы кнопки сдвинулись влево

        # Основной вертикальный лэйаут формы
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Форма объекта"))  # заголовок формы
        layout.addLayout(form)                      # поля формы
        layout.addLayout(btns)                      # кнопки
        layout.addStretch(1)                        # чтобы всё вверх уложилось красиво

        # Подключаем клики кнопок к методам
        self.btn_save.clicked.connect(self._emit_save)  # при клике — отправляем сигнал
        self.btn_clear.clicked.connect(self.clear_form) # при клике — чистим форму

    def collect_data(self) -> dict:
        # Собираем данные из формы в словарь
        return {
            "id": self._id,  # сохраняем id, чтобы знать редактируемый элемент
            "title": self.le_title.text().strip(),
            "description": self.te_description.toPlainText().strip(),
            "tags": self.le_tags.text().strip(),
        }

    def fill_form(self, obj: dict):
        # Заполняем форму данными из объекта
        self._id = obj.get("id")  # сохраняем id элемента
        self.le_title.setText(obj.get("title", ""))
        self.te_description.setPlainText(obj.get("description", ""))
        self.le_tags.setText(obj.get("tags", ""))

    def clear_form(self):
        # Чистим форму и сбрасываем id
        self._id = None
        self.le_title.clear()
        self.te_description.clear()
        self.le_tags.clear()

    def _emit_save(self):
        # Отправляем сигнал сохранения с текущими данными
        self.sigSaveRequested.emit(self.collect_data())
