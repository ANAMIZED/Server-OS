"""Simple in-process + durable memory store for agents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from server_os.config import settings


class MemoryStore:
    """Namespace-isolated key-value + simple list memory."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.root = (data_dir or settings.data_dir) / "memory"
        self.root.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, dict[str, Any]] = {}

    def _ns_path(self, namespace: str) -> Path:
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in namespace)
        return self.root / f"{safe}.json"

    def _load(self, namespace: str) -> dict[str, Any]:
        if namespace in self._cache:
            return self._cache[namespace]
        path = self._ns_path(namespace)
        if path.exists():
            data = json.loads(path.read_text())
        else:
            data = {}
        self._cache[namespace] = data
        return data

    def _save(self, namespace: str) -> None:
        path = self._ns_path(namespace)
        path.write_text(json.dumps(self._cache.get(namespace, {}), indent=2))

    def get(self, namespace: str, key: str, default: Any = None) -> Any:
        return self._load(namespace).get(key, default)

    def set(self, namespace: str, key: str, value: Any) -> None:
        data = self._load(namespace)
        data[key] = value
        self._save(namespace)

    def append(self, namespace: str, key: str, value: Any) -> None:
        data = self._load(namespace)
        lst = data.get(key, [])
        if not isinstance(lst, list):
            lst = [lst]
        lst.append(value)
        data[key] = lst
        self._save(namespace)

    def list_keys(self, namespace: str) -> list[str]:
        return list(self._load(namespace).keys())

    def dump(self, namespace: str) -> dict[str, Any]:
        return dict(self._load(namespace))
