class InMemoryStorage:
    def __init__(self):
        # Здесь храним все элементы: ключ — id, значение — словарь с данными
        self._items: dict[int, dict] = {}
        # Счётчик для генерации нового id
        self._next_id = 1

    def _assign_id(self) -> int:
        # Берём текущий id и увеличиваем счётчик
        nid = self._next_id
        self._next_id += 1
        return nid

    def create(self, data: dict) -> dict:
        # Создаём новый элемент, присваиваем id и сохраняем данные
        obj = {
            "id": self._assign_id(),
            "title": data.get("title", "").strip(),       # удаляем лишние пробелы
            "description": data.get("description", "").strip(),
            "tags": data.get("tags", "").strip(),
        }
        self._items[obj["id"]] = obj  # кладём в словарь
        return obj

    def get(self, item_id: int) -> dict | None:
        # Берём элемент по id, если нет — вернёт None
        return self._items.get(item_id)

    def list_all(self) -> list[dict]:
        # Возвращаем все элементы, отсортированные по id, чтобы порядок был предсказуемый
        return [self._items[k] for k in sorted(self._items.keys())]

    def update(self, item_id: int, data: dict) -> dict:
        # Обновляем элемент, если его нет — выбросим ошибку
        if item_id not in self._items:
            raise KeyError(f"id={item_id} не найден")
        obj = self._items[item_id]
        # Обновляем только те поля, которые передали
        if "title" in data:
            obj["title"] = (data["title"] or "").strip()
        if "description" in data:
            obj["description"] = (data["description"] or "").strip()
        if "tags" in data:
            obj["tags"] = (data["tags"] or "").strip()
        return obj

    def delete(self, item_id: int) -> None:
        # Удаляем элемент по id, если нет — просто ничего не делаем
        self._items.pop(item_id, None)

    def clear(self) -> None:
        # Чистим всё хранилище
        self._items.clear()
