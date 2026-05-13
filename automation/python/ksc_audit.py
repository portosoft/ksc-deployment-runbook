#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import paramiko
from dotenv import load_dotenv

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler("ksc_audit.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_audit(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    audit_points = [
        {"desc": "Sistema Operacional", "cmd": "hostnamectl | grep 'Operating System'"},
        {"desc": "Estado do PostgreSQL", "cmd": "systemctl is-active postgresql-16"},
        {"desc": "Portas KSC (13000/14000/13291)", "cmd": "ss -tulpn | grep -E '13000|14000|13291'"},
        {"desc": "Estado do SELinux", "cmd": "getenforce"},
        {"desc": "Binários KSC", "cmd": "ls -l /opt/kaspersky/ksc64/sbin/klserver"},
        {"desc": "Conectividade DB", "cmd": "sudo -u postgres psql -c 'SELECT version();'"}
    ]

    report = []
    try:
        logger.info(f"--- Iniciando Auditoria em {host} ---")
        client.connect(host, username=user, password=password, timeout=15)

        for point in audit_points:
            full_cmd = f"sudo -S {point['cmd']}"
            stdin, stdout, stderr = client.exec_command(full_cmd)
            stdin.write(password + '\n')
            stdin.flush()

            res = stdout.read().decode('utf-8').strip()
            status = stdout.channel.recv_exit_status()

            symbol = "✅" if status == 0 else "❌"
            logger.info(f"{symbol} {point['desc']}: {res if res else 'OK'}")
            report.append(f"{symbol} {point['desc']}: {res}")

        client.close()
        return report
    except Exception as e:
        logger.error(f"❌ Erro de Conexão: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="KSC 16 Audit Tool")
    parser.add_argument('--config', help="Caminho para o arquivo .env", default="configs/env/ksc_vars.env")
    parser.add_argument('--check', action='store_true', help="Executa a auditoria")
    parser.add_argument('--report', help="Gera um arquivo de relatório", metavar="FILE")

    args = parser.parse_args()

    if os.path.exists(args.config):
        load_dotenv(args.config)

    host = os.getenv('KSC_HOST')
    user = os.getenv('KSC_USER')
    password = os.getenv('KSC_PASS')

    if not all([host, user, password]):
        logger.error("Erro: Variáveis de ambiente incompletas.")
        sys.exit(2)

    if args.check or args.report:
        report_data = run_audit(host, user, password)

        if args.report and report_data:
            with open(args.report, 'w', encoding='utf-8') as f:
                f.write("\n".join(report_data))
            logger.info(f"\nRelatório salvo em: {args.report}")

        if report_data:
            sys.exit(0)
        else:
            sys.exit(3)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
