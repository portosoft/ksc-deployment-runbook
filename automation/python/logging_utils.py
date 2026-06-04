import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Literal

RunType = Literal["precheck", "deploy", "postcheck", "report"]


def init_evidence_dir(run_type: RunType) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = Path("evidence") / run_type / timestamp
    # 🛡️ Sentinel: Ensure audit logs are created with restricted permissions (0o700)
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
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
    fh = logging.FileHandler(evidence_dir / "run.log", encoding="utf-8")
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    return logger


def log_json(logger: logging.Logger, event: str, **fields) -> None:
    payload = {"event": event, "timestamp": datetime.utcnow().isoformat() + "Z"}
    payload.update(fields)
    logger.info(json.dumps(payload, ensure_ascii=False))
