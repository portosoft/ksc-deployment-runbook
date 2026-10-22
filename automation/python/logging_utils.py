import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Literal

from automation.python.utils.secure_file import make_secure_dir

RunType = Literal["precheck", "deploy", "postcheck", "report"]


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

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Arquivo JSON lines
    log_file = evidence_dir / "run.log"
    # Create the file with strict permissions
    if not log_file.exists():
        log_file.touch(mode=0o600)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    return logger


def log_json(logger: logging.Logger, event: str, **fields) -> None:
    """Registra um evento estruturado em JSON Lines com timestamp UTC.

    Args:
        logger: Logger configurado.
        event: Nome do evento.
        **fields: Campos adicionais para incluir no payload JSON.
    """
    payload = {"event": event, "timestamp": datetime.utcnow().isoformat() + "Z"}
    payload.update(fields)
    logger.info(json.dumps(payload, ensure_ascii=False))
