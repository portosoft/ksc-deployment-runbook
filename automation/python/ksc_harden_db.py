#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import paramiko
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def apply_hardening(host, user, password, apply=False):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    harden_cmds = [
        'sed -i "s/^#max_connections = .*/max_connections = 1000/" /var/lib/pgsql/16/data/postgresql.conf',
        "grep -q 'shared_preload_libraries' /var/lib/pgsql/16/data/postgresql.conf || echo \"shared_preload_libraries = 'pg_stat_statements'\" >> /var/lib/pgsql/16/data/postgresql.conf",
        "systemctl restart postgresql-16",
    ]

    try:
        logger.info(f"Conectando a {host} para hardening...")
        client.connect(host, username=user, password=password, timeout=15)

        for cmd in harden_cmds:
            if not apply:
                logger.info(f"[CHECK] Verificando comando: {cmd}")
                continue

            logger.info(f"Aplicando: {cmd}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}")
            stdin.write(password + "\n")
            stdin.flush()
            status = stdout.channel.recv_exit_status()
            if status != 0:
                logger.error(f"Falha ao aplicar hardening: {cmd}")

        client.close()
        return True
    except Exception as e:
        logger.error(f"Erro: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="KSC 16 DB Hardening Tool")
    parser.add_argument(
        "--config", help="Arquivo .env", default="configs/env/ksc_vars.env"
    )
    parser.add_argument("--check", action="store_true", help="Apenas simula mudanças")
    parser.add_argument("--apply", action="store_true", help="Aplica o hardening")

    args = parser.parse_args()

    if os.path.exists(args.config):
        load_dotenv(args.config)

    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    if not all([host, user, password]):
        logger.error("Erro: Credenciais incompletas.")
        sys.exit(2)

    if args.apply:
        if apply_hardening(host, user, password, apply=True):
            logger.info("Hardening concluído com sucesso.")
            sys.exit(0)
        else:
            sys.exit(3)
    elif args.check:
        apply_hardening(host, user, password, apply=False)
        sys.exit(0)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
