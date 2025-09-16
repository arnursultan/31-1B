class InMemoryStorage:
    def __init__(self):
        self._items: dict[int, dict] = {}
        self._next_id = 1

    def _assign_id(self) -> int:
        nid = self._next_id
        self._next_id += 1
        return nid

    def create(self, data: dict) -> dict:
        obj = {
            "id": self._assign_id(),
            "title": data.get("title", "").strip(),
            "description": data.get("description", "").strip(),
            "tags": data.get("tags", "").strip(),
        }
        self._items[obj["id"]] = obj
        return obj

    def get(self, item_id: int) -> dict | None:
        return self._items.get(item_id)

    def list_all(self) -> list[dict]:
        return [self._items[k] for k in sorted(self._items.keys())]

    def update(self, item_id: int, data: dict) -> dict:
        if item_id not in self._items:
            raise KeyError(f"id={item_id} не найден")
        obj = self._items[item_id]
        if "title" in data:
            obj["title"] = (data["title"] or "").strip()
        if "description" in data:
            obj["description"] = (data["description"] or "").strip()
        if "tags" in data:
            obj["tags"] = (data["tags"] or "").strip()
        return obj

    def delete(self, item_id: int) -> None:
        self._items.pop(item_id, None)

    def clear(self) -> None:
        self._items.clear()
