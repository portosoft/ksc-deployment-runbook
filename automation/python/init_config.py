"""
automation/python/init_config.py
Interactive CLI for securely filling production environment variables.

Usage:
    python3 -m automation.python.init_config [--vault]
"""

import argparse
import getpass
import pathlib
import sys

from pydantic import ValidationError

from automation.python.config import KscConfig, ConfigError
from automation.python.utils.secure_file import write_secure_file
from automation.lib import vault

# ---------------------------------------------------------------------------
# Field definitions
# ---------------------------------------------------------------------------

# Non-sensitive fields: collected via input() with default shown
NON_SENSITIVE_FIELDS = [
    ("KSC_DB_HOST",      "127.0.0.1"),
    ("KSC_DB_PORT",      "5432"),
    ("KSC_DB_USER",      "kluser"),
    ("KSC_FQDN",         "ksc-placeholder.test"),
    ("KSC_HOST",         "127.0.0.1"),
    ("KSC_USER",         "suporte"),
    ("KSC_WEB_PORT",     "443"),
    ("KSC_SELINUX_MODE", "enforcing"),
]

# Sensitive fields: collected via getpass (no default shown)
SENSITIVE_FIELDS = [
    "KSC_DB_PASS",
    "KSC_ADMIN_PASS",
    "KSC_PASS",
]

# Keys whose values must never be shown in diff output
_SENSITIVE_KEY_SUFFIXES = ("PASS", "PASSWORD")

ENV_FILE_PATH = pathlib.Path("configs/env/ksc_vars.env")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_sensitive_key(key: str) -> bool:
    """Return True if the key name ends with a known sensitive suffix.

    Args:
        key: Nome da chave a ser verificada (ex.: ``KSC_DB_PASS``).

    Returns:
        True se o nome da chave terminar com algum dos sufixos
        definidos em ``_SENSITIVE_KEY_SUFFIXES``.
    """
    upper = key.upper()
    return any(upper.endswith(suffix) for suffix in _SENSITIVE_KEY_SUFFIXES)


def _parse_env_file(path: pathlib.Path) -> dict:
    """Parse a KEY=value env file into a dict, skipping comments and blanks.

    Args:
        path: Caminho para o arquivo .env a ser parseado.

    Returns:
        Dicionário mapping variable names to their values (stripped of quotes).
        Retorna dict vazio se o arquivo não existir.
    """
    result = {}
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    result[key.strip()] = value.strip().strip("\"'")
    except FileNotFoundError:
        pass
    return result


def _render_env_content(values: dict) -> str:
    """Render a dict into KEY=value lines suitable for a .env file.

    Args:
        values: Dicionário com pares chave=valor.

    Returns:
        String no formato ``KEY=value\\n`` para cada entrada, com uma
        quebra de linha final.
    """
    lines = []
    for key, value in values.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _build_ksc_config(values: dict) -> KscConfig:
    """Constrói um :class:`KscConfig` a partir do dicionário de valores coletados.

    Valida e converte tipos (portas como int, senhas como str não vazia)
    antes de instanciar o modelo.

    Args:
        values: Dicionário com as variáveis de ambiente coletadas.

    Returns:
        Instância de :class:`KscConfig` populada.

    Raises:
        ConfigError: Se ``KSC_DB_PORT`` ou ``KSC_WEB_PORT`` não forem
            inteiros válidos, ou se ``KSC_DB_PASS`` / ``KSC_ADMIN_PASS``
            estiverem vazias.
    """
    try:
        db_port = int(values.get("KSC_DB_PORT", "5432"))
    except ValueError:
        raise ConfigError("KSC_DB_PORT deve ser um inteiro")

    try:
        web_port = int(values.get("KSC_WEB_PORT", "443"))
    except ValueError:
        raise ConfigError("KSC_WEB_PORT deve ser um inteiro")

    db_password = values.get("KSC_DB_PASS", "")
    if not db_password:
        raise ConfigError("KSC_DB_PASS é obrigatória")

    ksc_admin_password = values.get("KSC_ADMIN_PASS", "")
    if not ksc_admin_password:
        raise ConfigError("KSC_ADMIN_PASS é obrigatória")

    return KscConfig(
        db_host=values.get("KSC_DB_HOST", "127.0.0.1"),
        db_port=db_port,
        db_user=values.get("KSC_DB_USER", "kluser"),
        db_password=db_password,
        ksc_admin_password=ksc_admin_password,
        web_port=web_port,
        selinux_expected_mode=values.get("KSC_SELINUX_MODE", "enforcing"),
        ksc_host=values.get("KSC_HOST", "127.0.0.1"),
        ksc_user=values.get("KSC_USER", "suporte"),
        ksc_pass=values.get("KSC_PASS") or None,
        ksc_fqdn=values.get("KSC_FQDN", "ksc-placeholder.test"),
    )


# ---------------------------------------------------------------------------
# Collection loop
# ---------------------------------------------------------------------------

def _collect_all_fields() -> dict:
    """Coleta interativamente todos os campos do operador via stdin.

    Re-prompts any field whose collected set fails KscConfig validation.

    O loop externo repete a coleta completa sempre que a validação
    via :func:`_build_ksc_config` falhar, garantindo que apenas valores
    válidos sejam aceitos.

    Returns:
        Dicionário mapping env key → value (ex.: ``{"KSC_DB_HOST": "127.0.0.1"}``).
    """
    values: dict = {}

    # We run in a loop so that on validation failure we can re-prompt
    # just the offending field(s). To keep it simple, on any validation
    # error we show the message and restart collection of ALL fields so
    # the operator can correct the problem (re-entering a wrong FQDN is
    # cheap and avoids complex per-field error routing in pydantic v2).
    while True:
        # Collect non-sensitive fields
        for field, default in NON_SENSITIVE_FIELDS:
            while True:
                raw = input(f"{field} [{default}]: ").strip()
                value = raw if raw else default
                # Pre-validate port fields immediately for better UX
                if field in ("KSC_DB_PORT", "KSC_WEB_PORT"):
                    try:
                        int(value)
                        values[field] = value
                        break
                    except ValueError:
                        print(f"Valor inválido: {field} deve ser um inteiro")
                else:
                    values[field] = value
                    break

        # Collect sensitive fields
        for field in SENSITIVE_FIELDS:
            while True:
                value = getpass.getpass(f"{field}: ").strip()
                values[field] = value
                break

        # Validate the complete set via KscConfig
        try:
            _build_ksc_config(values)
            break  # Validation passed — exit the outer loop
        except (ValidationError, ConfigError) as exc:
            msg = _extract_error_message(exc)
            print(f"Valor inválido: {msg}")
            print("Por favor, preencha os campos novamente.\n")
            values = {}
            continue

    return values


def _extract_error_message(exc: Exception) -> str:
    """Extrai uma mensagem legível de uma exceção de validação.

    Suporta :class:`ConfigError` (retorna a mensagem direta) e
    :class:`ValidationError` do Pydantic (extrai e concatena os erros
    de campo). Para qualquer outra exceção, retorna ``str(exc)``.

    Args:
        exc: Instância de exceção a ser processada.

    Returns:
        Mensagem de erro formatada como string legível.
    """
    if isinstance(exc, ConfigError):
        return str(exc)
    if isinstance(exc, ValidationError):
        errors = []
        for err in exc.errors():
            loc = ".".join(str(x) for x in err["loc"])
            errors.append(f"{loc}: {err['msg']}")
        return "; ".join(errors)
    return str(exc)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Ponto de entrada principal do CLI interativo de configuração.

    Fluxo:
        1. Se o arquivo ``configs/env/ksc_vars.env`` já existir, exibe
           um diff de chaves e solicita confirmação antes de sobrescrever.
        2. Coleta todos os campos (sensíveis e não-sensíveis) interativamente.
        3. Escreve o arquivo .env com permissão ``0o600``.
        4. Opcionalmente (com ``--vault``), cifra os campos sensíveis.

    Uso:
        ``python3 -m automation.python.init_config [--vault]``
    """
    parser = argparse.ArgumentParser(
        description="Preenche interativamente as variáveis de ambiente de produção."
    )
    parser.add_argument(
        "--vault",
        action="store_true",
        help="Após escrever o .env, cifra os campos sensíveis em configs/secrets.bin",
    )
    args = parser.parse_args()

    # --- Check if file already exists and show diff / confirm ---
    if ENV_FILE_PATH.exists():
        # We need to collect values first to show the diff, but we also need
        # the diff before collecting. The design flow says: show diff → confirm
        # → then collect. We show the diff of KEYS only (no values needed yet),
        # comparing the existing keys to the full expected key set.
        all_expected_keys = [f for f, _ in NON_SENSITIVE_FIELDS] + SENSITIVE_FIELDS
        existing = _parse_env_file(ENV_FILE_PATH)

        # Show diff and ask for confirmation
        confirmed = _show_diff_and_confirm_keys_only(
            ENV_FILE_PATH, existing, set(all_expected_keys)
        )
        if not confirmed:
            print("Operação cancelada. Nenhum arquivo foi modificado.")
            sys.exit(0)

    # --- Collect all fields interactively ---
    values = _collect_all_fields()

    # --- Write the env file ---
    content = _render_env_content(values)
    try:
        write_secure_file(str(ENV_FILE_PATH), content, mode=0o600)
    except OSError as exc:
        print(str(exc))
        sys.exit(1)

    print(f"\nArquivo '{ENV_FILE_PATH}' escrito com sucesso (0o600).")

    # --- Optional vault encryption ---
    if args.vault:
        sensitive_values = {k: values[k] for k in SENSITIVE_FIELDS}
        vault.encrypt_secrets(sensitive_values)
        print("Segredos cifrados gravados em 'configs/secrets.bin' (0o600).")


def _show_diff_and_confirm_keys_only(
    existing_path: pathlib.Path,
    existing: dict,
    new_keys: set,
) -> bool:
    """Exibe diff de chaves e solicita confirmação antes de sobrescrever.

    Compara as chaves do arquivo existente com o conjunto esperado de
    chaves. Para chaves em comum com sufixo sensível, o valor não é
    exibido. Chaves adicionadas são marcadas com ``[+]``, removidas com
    ``[-]`` e alteradas com ``[~]``.

    Args:
        existing_path: Caminho do arquivo .env existente.
        existing: Dicionário com as chaves/valores atuais.
        new_keys: Conjunto de chaves esperadas no novo arquivo.

    Returns:
        True se o operador confirmar a sobrescrita (responder "s" ou "S").
    """
    existing_keys = set(existing.keys())

    added = sorted(new_keys - existing_keys)
    removed = sorted(existing_keys - new_keys)
    # Keys present in both — will be re-entered so they're "changed"
    # We only flag them as changed if they carry a sensitive suffix
    # (we can't know the new value yet). We show all common keys as potentially changed.
    common = sorted(existing_keys & new_keys)

    has_diff = bool(added or removed)

    if has_diff or common:
        print(f"\nDiff de chaves em relação a '{existing_path}':")
        for k in added:
            print(f"  [+] {k}  (nova chave)")
        for k in removed:
            print(f"  [-] {k}  (será removida)")
        for k in common:
            if _is_sensitive_key(k):
                print(f"  [~] {k}  (valor sensível — não exibido; será substituído)")
            else:
                print(f"  [~] {k} = {existing[k]!r}  (será substituído)")
    else:
        print("Nenhuma alteração de chaves detectada em relação ao arquivo existente.")

    answer = input("\nO arquivo já existe. Deseja sobrescrever? [s/N]: ").strip()
    return answer in ("s", "S")


if __name__ == "__main__":
    main()
