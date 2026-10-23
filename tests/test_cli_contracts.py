import subprocess
import sys
from pathlib import Path


def run_script(module_name: str, args: list, cwd: str = None) -> subprocess.CompletedProcess:
    import os

    cmd = [sys.executable, "-m", module_name] + args
    # Define a variável de ambiente PYTHONPATH para o diretório raiz do projeto, preservando o restante do ambiente
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent)
    return subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd)


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


def test_packages_help():
    result = run_script("automation.python.kscctl", ["packages", "--help"])
    assert result.returncode == 0
    assert "--list" in result.stdout
    assert "--verify-dir" in result.stdout
    assert "--download" in result.stdout


def test_packages_list():
    result = run_script("automation.python.kscctl", ["packages", "--list"])
    assert result.returncode == 0
    assert "ksc-server-16.3-pt-BR" in result.stdout
    assert "kesl-distributive-12.5" in result.stdout


def test_kscctl_help_has_config_and_verbose():
    """Valida se kscctl --help exibe as opções globais --config e --verbose."""
    result = run_script("automation.python.kscctl", ["--help"])
    assert result.returncode == 0
    assert "--config" in result.stdout
    assert "--verbose" in result.stdout


def test_kscctl_custom_config_flag(tmp_path):
    """Valida se kscctl aceita e carrega um arquivo .env customizado via --config."""
    from automation.python.credentials import generate_password

    custom_env = tmp_path / "custom.env"
    custom_env.write_text(
        f"KSC_DB_PASS={generate_password()}\n"
        f"KSC_ADMIN_PASS={generate_password()}\n"
        "KSC_DB_HOST=127.0.0.1\n"
        "KSC_HOST=127.0.0.1\n",
        encoding="utf-8",
    )

    result = run_script(
        "automation.python.kscctl",
        ["--config", str(custom_env), "audit", "--check"],
    )
    # returncode != 2 garante que o arquivo de configuração foi carregado com sucesso (exit code 2 é ConfigError)
    assert result.returncode != 2
    assert "Configuração inválida" not in result.stderr


def test_kscctl_execution_from_subdirectory():
    """Valida que a execução de kscctl a partir de um subdiretório localiza a configuração na raiz do projeto."""
    from automation.python.config import DEFAULT_ENV_PATH
    from automation.python.credentials import generate_password

    env_existed = DEFAULT_ENV_PATH.exists()
    if not env_existed:
        DEFAULT_ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_ENV_PATH.write_text(
            f"KSC_DB_PASS={generate_password()}\n"
            f"KSC_ADMIN_PASS={generate_password()}\n"
            "KSC_DB_HOST=127.0.0.1\n"
            "KSC_HOST=127.0.0.1\n",
            encoding="utf-8",
        )
    try:
        sub_dir = Path(__file__).parent  # tests/ directory
        result = run_script(
            "automation.python.kscctl",
            ["audit", "--check"],
            cwd=str(sub_dir),
        )
        # Não deve falhar com "Arquivo de ambiente não encontrado" nem exit code 2
        assert result.returncode != 2
        assert "Arquivo de ambiente não encontrado" not in result.stderr
    finally:
        if not env_existed and DEFAULT_ENV_PATH.exists():
            DEFAULT_ENV_PATH.unlink()
