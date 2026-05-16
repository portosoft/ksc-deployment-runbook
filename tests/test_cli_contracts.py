import subprocess
import sys
from pathlib import Path


def run_script(module_name: str, args: list) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", module_name] + args
    # Define a variável de ambiente PYTHONPATH para o diretório raiz do projeto
    env = {"PYTHONPATH": str(Path(__file__).parent.parent)}
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def test_audit_help():
    result = run_script("automation.python.ksc_audit", ["--help"])
    assert result.returncode == 0
    assert "--check" in result.stdout
    assert "--postcheck" in result.stdout
    assert "--report" in result.stdout


def test_setup_help():
    result = run_script("automation.python.ksc_setup", ["--help"])
    assert result.returncode == 0
    assert "--check" in result.stdout
    assert "--apply" in result.stdout


def test_audit_missing_args():
    result = run_script("automation.python.ksc_audit", [])
    assert result.returncode != 0
    assert (
        "required" in result.stderr.lower()
        or "esperado" in result.stderr.lower()
        or "error:" in result.stderr.lower()
    )


def test_setup_missing_args():
    result = run_script("automation.python.ksc_setup", [])
    assert result.returncode != 0
    assert (
        "required" in result.stderr.lower()
        or "esperado" in result.stderr.lower()
        or "error:" in result.stderr.lower()
    )
