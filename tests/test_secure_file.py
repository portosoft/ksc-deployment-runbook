import os
import sys
import stat
import pytest
from pathlib import Path
from automation.python.utils.secure_file import (
    write_secure_file,
    make_secure_dir,
    temp_secure_file,
    assert_secure,
)

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="POSIX file permissions are not supported on Windows"
)


def test_write_secure_file(tmp_path):
    path = tmp_path / "secret.txt"
    content = "test file content"
    write_secure_file(str(path), content, 0o600)

    assert path.read_text() == content
    actual_mode = stat.S_IMODE(os.stat(str(path)).st_mode)
    assert actual_mode == 0o600


def test_make_secure_dir(tmp_path):
    path = tmp_path / "secure_dir"
    # First create it normally, maybe with umask
    path.mkdir()
    os.chmod(str(path), 0o755)

    make_secure_dir(path, 0o700)
    actual_mode = stat.S_IMODE(os.stat(str(path)).st_mode)
    assert actual_mode == 0o700


def test_temp_secure_file():
    content = "test temp content"
    with temp_secure_file(content, 0o600) as path:
        assert os.path.exists(path)
        with open(path, "r") as f:
            assert f.read() == content
        actual_mode = stat.S_IMODE(os.stat(path).st_mode)
        assert actual_mode == 0o600
    # ensure it is deleted
    assert not os.path.exists(path)


def test_assert_secure(tmp_path):
    path = tmp_path / "test.txt"
    path.write_text("test")
    os.chmod(str(path), 0o644)

    with pytest.raises(PermissionError, match="Insecure permissions"):
        assert_secure(str(path), 0o600)

    os.chmod(str(path), 0o600)
    assert_secure(str(path), 0o600)  # should not raise
