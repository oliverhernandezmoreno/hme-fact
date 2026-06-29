import shutil
import tempfile
import uuid

import pytest

from app.services.storage import LocalFileStorageService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def storage_service() -> LocalFileStorageService:
    temp_dir = tempfile.mkdtemp()
    service = LocalFileStorageService(base_path=temp_dir)
    yield service
    shutil.rmtree(temp_dir)


async def test_local_storage_save_and_get(storage_service: LocalFileStorageService) -> None:
    company_id = uuid.uuid4()
    path = f"companies/{company_id}/test_file.txt"
    content = b"Hello world"

    saved_path = await storage_service.save_file(path, content)
    assert saved_path == path

    retrieved = await storage_service.get_file(path)
    assert retrieved == content


async def test_local_storage_delete(storage_service: LocalFileStorageService) -> None:
    path = "test_delete.txt"
    content = b"To be deleted"

    await storage_service.save_file(path, content)
    await storage_service.delete_file(path)

    with pytest.raises(FileNotFoundError):
        await storage_service.get_file(path)
