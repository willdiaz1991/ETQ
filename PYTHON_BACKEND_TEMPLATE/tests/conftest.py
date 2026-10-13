import os
from unittest.mock import patch

os.environ["DB_SGL"] = "oracle://user:pass@localhost/dbname"
os.environ["SiKeyVault"] = "false"
os.environ["AES_KEY"] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
os.environ["AES_IV"] = "AAAAAAAAAAAAAAAAAAAAAA=="
os.environ["LOG_LEVEL"] = "DEBUG"

patch_decrypt = patch(
    "infrastructure.database.decrypt.decrypt",
    side_effect=lambda x: os.getenv(x.replace("DB_", "")) or "oracle://user:pass@localhost/dbname",
)
patch_decrypt.start()


def pytest_sessionfinish(session, exitstatus):  # pragma: no cover
    """Stop patches after the test session ends."""
    patch_decrypt.stop()
