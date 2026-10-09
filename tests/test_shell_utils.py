import pytest
from automation.python.shell_utils import ShellCommandError, run_command


def test_shell_command_error_init():
    cmd = ["echo", "test"]
    error = ShellCommandError(cmd=cmd, returncode=1, stdout="out", stderr="err")
    assert str(error) == "Command failed: echo test"
    assert error.cmd == cmd
    assert error.returncode == 1
    assert error.stdout == "out"
    assert error.stderr == "err"


def test_run_command_success():
    stdout, stderr, rc = run_command(["echo", "hello"], check=True)
    assert rc == 0
    assert stdout.strip() == "hello"
    assert stderr == ""


def test_run_command_failure_check_true():
    with pytest.raises(ShellCommandError) as exc_info:
        run_command(["ls", "/non_existent_file_path_12345"], check=True)

    assert exc_info.value.returncode != 0
    assert exc_info.value.cmd == ["ls", "/non_existent_file_path_12345"]
    assert "No such file or directory" in exc_info.value.stderr or "non_existent_file_path_12345" in exc_info.value.stderr


def test_run_command_failure_check_false():
    stdout, stderr, rc = run_command(["ls", "/non_existent_file_path_12345"], check=False)
    assert rc != 0
    assert "No such file or directory" in stderr or "non_existent_file_path_12345" in stderr


def test_run_command_file_not_found():
    with pytest.raises(ShellCommandError) as exc_info:
        run_command(["/non_existent_executable_12345"], check=True)

    assert exc_info.value.returncode == 127
    assert exc_info.value.stderr == "Command not found: /non_existent_executable_12345"
    assert exc_info.value.cmd == ["/non_existent_executable_12345"]


def test_run_command_file_not_found_check_false():
    stdout, stderr, rc = run_command(["/non_existent_executable_12345"], check=False)
    assert rc == 127
    assert stdout == ""
    assert stderr == "Command not found: /non_existent_executable_12345"
