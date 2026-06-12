import os
import stat
import tempfile
import contextlib
from pathlib import Path


def write_secure_file(path: str, content: str, mode: int = 0o600) -> None:
    """Atomic, permission-safe file write."""
    dir_path = os.path.dirname(path) or "."
    fd, temp_path = tempfile.mkstemp(dir=dir_path, text=True)

    try:
        # Set permissions securely
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w") as f:
            f.write(content)
        # Atomically replace the target file
        os.replace(temp_path, path)
    except Exception:
        # Clean up temp file on failure
        if os.path.exists(temp_path):
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
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w") as f:
            f.write(content)
        yield temp_path
    finally:
        if os.path.exists(temp_path):
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
