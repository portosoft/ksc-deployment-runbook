import os
import shutil
from dataclasses import dataclass
from typing import List, Optional

from .shell_utils import run_command
from .config import KscConfig

SUPPORTED_ID = {"rocky", "ol", "ol9", "oracle", "rhel"}
SUPPORTED_MAJOR_VERSION = {9}
DEFAULT_PORTS = [13000, 14000, 443]

MIN_RAM_MB = 8 * 1024
RECOMMENDED_RAM_MB = 16 * 1024
MIN_DISK_OPT_GB = 100
MIN_DISK_VAROPT_GB = 100


@dataclass
class CheckItem:
    name: str
    status: str  # "ok" | "warning" | "critical"
    message: str


@dataclass
class CheckResult:
    items: List[CheckItem]

    @property
    def has_critical(self) -> bool:
        return any(i.status == "critical" for i in self.items)

    def add(self, item: CheckItem) -> None:
        self.items.append(item)


def _get_total_ram_mb() -> int:
    with open("/proc/meminfo", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                parts = line.split()
                kb = int(parts[1])
                return kb // 1024
    raise RuntimeError("Não foi possível determinar a RAM total.")


def _get_disk_gb(path: str) -> int:
    usage = shutil.disk_usage(path)
    return usage.free // (1024 * 1024 * 1024)


def check_ram_and_disk(config: KscConfig) -> CheckResult:
    result = CheckResult(items=[])
    is_ci = os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("KSC_SKIP_RESOURCE_CHECK") == "true"

    # RAM
    try:
        total_ram_mb = _get_total_ram_mb()
        if total_ram_mb < MIN_RAM_MB:
            status = "warning" if is_ci else "critical"
            msg = f"RAM total {total_ram_mb} MB abaixo do mínimo ({MIN_RAM_MB} MB)."
            if is_ci:
                msg += " (Tratado como warning em ambiente CI/mock)."
        elif total_ram_mb < RECOMMENDED_RAM_MB:
            status = "warning"
            msg = f"RAM total {total_ram_mb} MB abaixo da recomendação ({RECOMMENDED_RAM_MB} MB)."
        else:
            status = "ok"
            msg = f"RAM total {total_ram_mb} MB adequada."
        result.add(CheckItem(name="ram_total", status=status, message=msg))
    except Exception as exc:
        result.add(
            CheckItem(name="ram_total", status="warning" if is_ci else "critical", message=f"Falha: {exc}")
        )

    # Disco /opt
    try:
        opt_gb = _get_disk_gb("/opt")
        if opt_gb < MIN_DISK_OPT_GB:
            status = "warning" if is_ci else "critical"
            msg = (
                f"Espaço em /opt ({opt_gb} GB) abaixo do mínimo ({MIN_DISK_OPT_GB} GB)."
            )
            if is_ci:
                msg += " (Tratado como warning em ambiente CI/mock)."
        else:
            status = "ok"
            msg = f"Espaço em /opt ({opt_gb} GB) adequado."
        result.add(CheckItem(name="disk_opt", status=status, message=msg))
    except Exception as exc:
        result.add(
            CheckItem(name="disk_opt", status="warning" if is_ci else "critical", message=f"Falha: {exc}")
        )

    # Disco /var/opt
    try:
        varopt_gb = _get_disk_gb("/var/opt")
        if varopt_gb < MIN_DISK_VAROPT_GB:
            status = "warning" if is_ci else "critical"
            msg = f"Espaço em /var/opt ({varopt_gb} GB) abaixo do mínimo ({MIN_DISK_VAROPT_GB} GB)."
            if is_ci:
                msg += " (Tratado como warning em ambiente CI/mock)."
        else:
            status = "ok"
            msg = f"Espaço em /var/opt ({varopt_gb} GB) adequado."
        result.add(CheckItem(name="disk_varopt", status=status, message=msg))
    except Exception as exc:
        result.add(
            CheckItem(name="disk_varopt", status="warning" if is_ci else "critical", message=f"Falha: {exc}")
        )

    return result


def _read_os_release() -> dict:
    data = {}
    try:
        with open("/etc/os-release", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                data[key] = value.strip().strip('"')
    except FileNotFoundError:
        raise RuntimeError("/etc/os-release não encontrado.")
    return data


def check_os_version() -> CheckResult:
    result = CheckResult(items=[])
    try:
        os_release = _read_os_release()
        os_id = os_release.get("ID", "").lower()
        version_id = os_release.get("VERSION_ID", "")
        major = int(version_id.split(".", 1)[0]) if version_id else 0

        if os_id not in SUPPORTED_ID:
            result.add(
                CheckItem(
                    name="os_id",
                    status="critical",
                    message=f"SO não suportado: {os_id}",
                )
            )
        elif major not in SUPPORTED_MAJOR_VERSION:
            result.add(
                CheckItem(
                    name="os_version",
                    status="critical",
                    message=f"Versão major não suportada: {version_id}",
                )
            )
        else:
            result.add(
                CheckItem(
                    name="os_version",
                    status="ok",
                    message=f"SO suportado: {os_id} {version_id}",
                )
            )
    except Exception as exc:
        result.add(
            CheckItem(name="os_version", status="critical", message=f"Falha: {exc}")
        )
    return result


def _get_selinux_mode() -> str:
    try:
        stdout, _, rc = run_command(["getenforce"], check=False)
        if rc != 0:
            return "unknown"
        return stdout.strip().lower()
    except Exception:
        return "unknown"


def check_selinux(config: KscConfig, is_postcheck: bool = False) -> CheckResult:
    result = CheckResult(items=[])
    mode = _get_selinux_mode()
    if mode == "unknown":
        result.add(
            CheckItem(
                name="selinux",
                status="critical" if is_postcheck else "warning",
                message="Não foi possível determinar o modo.",
            )
        )
        return result

    expected = config.selinux_expected_mode.lower()
    if mode != expected:
        result.add(
            CheckItem(
                name="selinux",
                status="critical" if is_postcheck else "warning",
                message=f"SELinux '{mode}'. Esperado: '{expected}'.",
            )
        )
    else:
        result.add(
            CheckItem(name="selinux", status="ok", message=f"SELinux em modo '{mode}'.")
        )
    return result


def _get_listening_ports() -> List[int]:
    stdout, _, rc = run_command(["ss", "-lnt"], check=False)
    if rc != 0:
        return []

    ports = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("State"):
            continue
        parts = line.split()
        local_addr = parts[3] if len(parts) > 3 else ""
        if ":" in local_addr:
            port_str = local_addr.rsplit(":", 1)[-1]
            try:
                ports.append(int(port_str))
            except ValueError:
                continue
    return ports


def check_ports(config: KscConfig) -> CheckResult:
    result = CheckResult(items=[])
    ports_in_use = _get_listening_ports()

    ports_to_check = DEFAULT_PORTS.copy()
    if config.web_port not in ports_to_check:
        ports_to_check.append(config.web_port)

    for port in ports_to_check:
        if port in ports_in_use:
            result.add(
                CheckItem(
                    name=f"port_{port}",
                    status="critical",
                    message=f"Porta {port} em uso.",
                )
            )
        else:
            result.add(
                CheckItem(
                    name=f"port_{port}", status="ok", message=f"Porta {port} livre."
                )
            )
    return result


def run_precheck(config: KscConfig) -> CheckResult:
    aggregated = CheckResult(items=[])
    aggregated.items.extend(check_os_version().items)
    aggregated.items.extend(check_selinux(config).items)
    aggregated.items.extend(check_ports(config).items)
    aggregated.items.extend(check_ram_and_disk(config).items)
    return aggregated


def _systemd_is_active(unit: str) -> Optional[bool]:
    stdout, stderr, rc = run_command(["systemctl", "is-active", unit], check=False)
    if rc != 0:
        if "could not be found" in stderr.lower() or "not found" in stderr.lower():
            return None
        return False
    return stdout.strip() == "active"


def _check_tcp_port_open(port: int) -> bool:
    return port in _get_listening_ports()


def _check_db_select_1(config: KscConfig) -> bool:
    env = os.environ.copy()
    if config.db_password:
        env["PGPASSWORD"] = config.db_password

    conn_args = [
        "psql",
        "-h",
        config.db_host,
        "-p",
        str(config.db_port),
        "-U",
        config.db_user,
        "-d",
        config.db_name,
        "-t",
        "-c",
        "SELECT 1;",
    ]
    stdout, stderr, rc = run_command(conn_args, check=False)
    return rc == 0 and "1" in stdout


def check_services_and_db(config: KscConfig) -> CheckResult:
    result = CheckResult(items=[])

    pg_units = ["postgresql", "postgresql-16"]
    pg_status = None
    for unit in pg_units:
        status = _systemd_is_active(unit)
        if status is True:
            pg_status = True
            unit_name = unit
            break
        elif status is False:
            pg_status = False
            unit_name = unit
            break

    if pg_status is True:
        result.add(
            CheckItem(name="postgresql", status="ok", message=f"Ativo ({unit_name}).")
        )
    elif pg_status is False:
        result.add(
            CheckItem(
                name="postgresql", status="critical", message=f"Inativo ({unit_name})."
            )
        )
    else:
        result.add(
            CheckItem(
                name="postgresql", status="critical", message="Status desconhecido."
            )
        )

    for svc in ["klnagent_srv", "kladminserver_srv"]:
        status = _systemd_is_active(svc)
        if status is True:
            result.add(CheckItem(name=svc, status="ok", message=f"Ativo."))
        else:
            result.add(
                CheckItem(
                    name=svc, status="critical", message=f"Inativo ou não encontrado."
                )
            )

    if _check_db_select_1(config):
        result.add(
            CheckItem(
                name="db_query", status="ok", message="SELECT 1 executado com sucesso."
            )
        )
    else:
        result.add(
            CheckItem(name="db_query", status="critical", message="Falha no SELECT 1.")
        )

    return result


def check_web_console(config: KscConfig) -> CheckResult:
    result = CheckResult(items=[])
    if _check_tcp_port_open(config.web_port):
        result.add(
            CheckItem(
                name="web_console",
                status="ok",
                message=f"Porta {config.web_port} em LISTEN.",
            )
        )
    else:
        result.add(
            CheckItem(
                name="web_console",
                status="critical",
                message=f"Porta {config.web_port} fechada.",
            )
        )
    return result


def run_postcheck(config: KscConfig) -> CheckResult:
    aggregated = CheckResult(items=[])
    aggregated.items.extend(check_services_and_db(config).items)
    aggregated.items.extend(check_web_console(config).items)
    aggregated.items.extend(check_selinux(config, is_postcheck=True).items)
    return aggregated
