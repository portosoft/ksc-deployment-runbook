import contextlib
import os
import stat
import tempfile
from pathlib import Path


def write_secure_file(path: str, content: str, mode: int = 0o600) -> None:
    """Atomic, permission-safe file write."""
    dir_path = os.path.dirname(path) or "."
    fd, temp_path = tempfile.mkstemp(dir=dir_path, text=True)

    try:
        if hasattr(os, "fchmod"):
            os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            fd = -1
            f.write(content)
        if not hasattr(os, "fchmod"):
            os.chmod(temp_path, mode)
        os.replace(temp_path, path)
    except Exception:
        if fd != -1:
            os.close(fd)
        if os.path.exists(temp_path):
            with contextlib.suppress(PermissionError, FileNotFoundError):
                os.unlink(temp_path)
        raise


def make_secure_dir(path: Path, mode: int = 0o700) -> None:
    """Directory creation with enforced mode."""
    path.mkdir(parents=True, exist_ok=True, mode=mode)
    # Ensure mode on existing dirs
    os.chmod(path, mode)


@contextlib.contextmanager
def temp_secure_file(content: str, mode: int = 0o600):
    """Context manager for ephemeral secret files."""
    fd, temp_path = tempfile.mkstemp(text=True)
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            fd = -1
            f.write(content)
        if not hasattr(os, "fchmod"):
            os.chmod(temp_path, mode)
        yield temp_path
    finally:
        if fd != -1:
            with contextlib.suppress(OSError):
                os.close(fd)
        if os.path.exists(temp_path):
            with contextlib.suppress(PermissionError, FileNotFoundError):
                os.unlink(temp_path)


def verify_permissions(path: str, expected_mode: int) -> bool:
    """Verify permissions."""
    if not os.path.exists(path):
        return False
    actual_mode = stat.S_IMODE(os.stat(path).st_mode)
    return actual_mode == expected_mode


def assert_secure(path: str, expected_mode: int) -> None:
    """Permission validation helper."""
    if not verify_permissions(path, expected_mode):
        actual_mode = stat.S_IMODE(os.stat(path).st_mode)
        raise PermissionError(
            f"Insecure permissions on {path}: expected {oct(expected_mode)}, got {oct(actual_mode)}"
        )
