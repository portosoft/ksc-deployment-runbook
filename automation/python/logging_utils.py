import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Literal

from automation.python.utils.secure_file import make_secure_dir

RunType = Literal["precheck", "deploy", "postcheck", "report"]


def init_evidence_dir(run_type: RunType) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = Path("evidence") / run_type / timestamp
    make_secure_dir(path, mode=0o700)
    return path


def configure_logger(evidence_dir: Path) -> logging.Logger:
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
    if not log_file.exists():
        import os
        with os.fdopen(os.open(log_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600), "w"):
            pass

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    return logger


def log_json(logger: logging.Logger, event: str, **fields) -> None:
    payload = {"event": event, "timestamp": datetime.utcnow().isoformat() + "Z"}
    payload.update(fields)
    logger.info(json.dumps(payload, ensure_ascii=False))
