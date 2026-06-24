from __future__ import annotations

import os
from abc import ABC, abstractmethod

from app.core.config import get_settings


class BaseFileStorageService(ABC):
    @abstractmethod
    async def save_file(self, path: str, content: bytes) -> str:
        pass

    @abstractmethod
    async def get_file(self, path: str) -> bytes:
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> None:
        pass


class LocalFileStorageService(BaseFileStorageService):
    def __init__(self, base_path: str) -> None:
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def _get_full_path(self, path: str) -> str:
        # Prevent directory traversal
        clean_path = os.path.normpath(path).lstrip("/")
        return os.path.join(self.base_path, clean_path)

    async def save_file(self, path: str, content: bytes) -> str:
        full_path = self._get_full_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(content)
        return path

    async def get_file(self, path: str) -> bytes:
        full_path = self._get_full_path(path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(full_path, "rb") as f:
            return f.read()

    async def delete_file(self, path: str) -> None:
        full_path = self._get_full_path(path)
        if os.path.exists(full_path):
            os.remove(full_path)


def get_file_storage_service() -> BaseFileStorageService:
    settings = get_settings()
    if settings.FILE_STORAGE_DRIVER == "local":
        return LocalFileStorageService(base_path=settings.LOCAL_STORAGE_PATH)
    raise ValueError(f"Unsupported storage driver: {settings.FILE_STORAGE_DRIVER}")
