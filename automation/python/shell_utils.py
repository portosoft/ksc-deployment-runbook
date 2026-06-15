import subprocess
from typing import List, Tuple


class ShellCommandError(Exception):
    def __init__(self, cmd: List[str], returncode: int, stdout: str, stderr: str):
        super().__init__(f"Command failed: {' '.join(cmd)}")
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def run_command(
    cmd: List[str], check: bool = True, capture_output: bool = True, env: dict = None
) -> Tuple[str, str, int]:
    """
    Executa comando via subprocess.
    Retorna (stdout, stderr, returncode).
    Se check=True e retorno != 0, lança ShellCommandError.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            env=env,
        )
        stdout = result.stdout if result.stdout else ""
        stderr = result.stderr if result.stderr else ""
        rc = result.returncode
    except FileNotFoundError:
        stdout = ""
        stderr = f"Command not found: {cmd[0]}"
        rc = 127

    if check and rc != 0:
        raise ShellCommandError(cmd, rc, stdout, stderr)

    return stdout, stderr, rc
