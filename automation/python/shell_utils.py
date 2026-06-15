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
    result = subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True,
        env=env,
    )

    stdout = result.stdout if result.stdout else ""
    stderr = result.stderr if result.stderr else ""

    if check and result.returncode != 0:
        raise ShellCommandError(cmd, result.returncode, stdout, stderr)

    return stdout, stderr, result.returncode
