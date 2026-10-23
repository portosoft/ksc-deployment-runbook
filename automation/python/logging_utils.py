import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Literal, Set

from automation.python.utils.secure_file import make_secure_dir

RunType = Literal["precheck", "deploy", "postcheck", "report"]

_REDACTION_SECRETS: Set[str] = set()


def set_redaction_secrets(secrets: Iterable[str]) -> None:
    """Registra credenciais e senhas a serem censuradas em logs."""
    global _REDACTION_SECRETS
    _REDACTION_SECRETS = {
        s for s in secrets if isinstance(s, str) and len(s.strip()) >= 3
    }


def add_redaction_secret(secret: str) -> None:
    """Adiciona uma credencial ao conjunto de segredos a censurar."""
    if isinstance(secret, str) and len(secret.strip()) >= 3:
        _REDACTION_SECRETS.add(secret)


def sanitize_text(text: str) -> str:
    """Substitui ocorrências de segredos registrados por ***REDACTED***."""
    if not isinstance(text, str):
        return text
    result = text
    for secret in _REDACTION_SECRETS:
        if secret in result:
            result = result.replace(secret, "***REDACTED***")
    return result


class SecretSanitizingFilter(logging.Filter):
    """Filtro de logging que remove segredos do registro antes de emitir."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = sanitize_text(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: sanitize_text(v) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    sanitize_text(v) if isinstance(v, str) else v for v in record.args
                )
        return True


def init_evidence_dir(run_type: RunType) -> Path:
    """Cria e retorna o Path do diretório de evidências para o tipo de execução.

    Cria a estrutura evidence/<run_type>/<timestamp> com permissões restritas (0o700).

    Args:
        run_type: Tipo de execução (precheck, deploy, postcheck, report).

    Returns:
        Path do diretório de evidências criado.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = Path("evidence") / run_type / timestamp
    # 🛡️ Sentinel: Ensure audit logs and their parent directories are created with restricted permissions (0o700)
    make_secure_dir(Path("evidence"), mode=0o700)
    make_secure_dir(path.parent, mode=0o700)
    make_secure_dir(path, mode=0o700)
    return path


def configure_logger(evidence_dir: Path) -> logging.Logger:
    """Configura o logger com handler de console e JSON Lines.

    O logger registra mensagens em formato texto no console e JSON Lines
    no arquivo run.log dentro do diretório de evidências.

    Args:
        evidence_dir: Diretório onde o arquivo de log será criado.

    Returns:
        Logger configurado.
    """
    logger = logging.getLogger(f"ksc_{evidence_dir.name}")
    logger.setLevel(logging.INFO)

    # Evitar handlers duplicados se chamar duas vezes
    if logger.handlers:
        return logger

    sanitizer = SecretSanitizingFilter()

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    ch.setFormatter(formatter)
    ch.addFilter(sanitizer)
    logger.addHandler(ch)

    # Arquivo JSON lines
    log_file = evidence_dir / "run.log"
    # Create the file with strict permissions
    if not log_file.exists():
        log_file.touch(mode=0o600)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.addFilter(sanitizer)
    logger.addHandler(fh)

    return logger


def log_json(logger: logging.Logger, event: str, **fields) -> None:
    """Registra um evento estruturado em JSON Lines com timestamp UTC sanitizado.

    Args:
        logger: Logger configurado.
        event: Nome do evento.
        **fields: Campos adicionais para incluir no payload JSON.
    """
    payload = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    for k, v in fields.items():
        if isinstance(v, str):
            payload[k] = sanitize_text(v)
        else:
            payload[k] = v
    logger.info(sanitize_text(json.dumps(payload, ensure_ascii=False)))
