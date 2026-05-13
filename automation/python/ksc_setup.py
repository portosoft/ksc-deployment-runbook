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
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ksc_setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_ssh_commands(host, user, password, commands, dry_run=False):
    if dry_run:
        for cmd in commands:
            logger.info(f"[DRY-RUN] Executaria: {cmd}")
        return []

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    results = []
    try:
        logger.info(f"Conectando ao host {host}...")
        client.connect(host, username=user, password=password, timeout=30)
        for cmd in commands:
            logger.info(f"Executando: {cmd}")
            full_cmd = f"sudo -S {cmd}"
            stdin, stdout, stderr = client.exec_command(full_cmd)
            stdin.write(password + '\n')
            stdin.flush()

            out = stdout.read().decode('utf-8').strip()
            err = stderr.read().decode('utf-8').strip()
            status = stdout.channel.recv_exit_status()

            results.append({'command': cmd, 'stdout': out, 'stderr': err, 'status': status})
            if status != 0:
                logger.error(f"Falha no comando: {cmd} (Status: {status})")
                if err: logger.error(f"Erro: {err}")
                break
        client.close()
    except Exception as e:
        logger.error(f"Erro de conexão ou execução SSH: {e}")
        return None
    return results

def validate_environment():
    required_vars = ['KSC_HOST', 'KSC_USER', 'KSC_PASS', 'KSC_DB_PASS']
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        logger.error(f"Variáveis de ambiente ausentes: {', '.join(missing)}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="KSC 16 Deployment Tool")
    parser.add_argument('--config', help="Caminho para o arquivo .env", default="configs/env/ksc_vars.env")
    parser.add_argument('--check', action='store_true', help="Apenas valida pré-requisitos")
    parser.add_argument('--apply', action='store_true', help="Executa a instalação real")
    parser.add_argument('--dry-run', action='store_true', help="Simula execução")

    args = parser.parse_args()

    # Carregar configuração
    if os.path.exists(args.config):
        load_dotenv(args.config)
    else:
        logger.warning(f"Arquivo de config {args.config} não encontrado. Usando env atual.")

    if not validate_environment():
        sys.exit(2) # Erro de configuração

    host = os.getenv('KSC_HOST')
    user = os.getenv('KSC_USER')
    password = os.getenv('KSC_PASS')
    db_pass = os.getenv('KSC_DB_PASS')
    fqdn = os.getenv('KSC_FQDN', host)

    if args.check:
        logger.info("--- Executando Validação de Pré-requisitos ---")
        check_cmds = [
            "hostname -f",
            "systemctl is-active postgresql-16",
            "sudo -u postgres psql -c 'SELECT 1' > /dev/null"
        ]
        results = run_ssh_commands(host, user, password, check_cmds)
        if results and all(r['status'] == 0 for r in results):
            logger.info("Validação concluída com sucesso. Pronto para instalar.")
            sys.exit(0)
        else:
            logger.error("Falha na validação de pré-requisitos.")
            sys.exit(1)

    if args.apply:
        logger.info("--- Iniciando Instalação do KSC ---")
        setup_cmds = [
            f"echo 'EULA_ACCEPTED=1' > /tmp/ans.txt",
            f"echo 'PP_ACCEPTED=1' >> /tmp/ans.txt",
            f"echo 'KSN_ACCEPTED=1' >> /tmp/ans.txt",
            f"echo 'KLSRV_UNATT_DBMS_TYPE=Postgres' >> /tmp/ans.txt", # Corrigido conforme README
            f"echo 'KLSRV_UNATT_DBMS_INSTANCE=127.0.0.1' >> /tmp/ans.txt",
            f"echo 'KLSRV_UNATT_DBMS_PORT=5432' >> /tmp/ans.txt",
            f"echo 'KLSRV_UNATT_DBMS_LOGIN=ksc_admin' >> /tmp/ans.txt", # Sugerido ksc_admin
            f"echo 'KLSRV_UNATT_DBMS_PASSWORD={db_pass}' >> /tmp/ans.txt",
            f"echo 'KLSRV_UNATT_DB_NAME=ksc' >> /tmp/ans.txt",
            f"echo 'KLSRV_UNATT_SERVERADDRESS={fqdn}' >> /tmp/ans.txt",
            "sudo -E bash -c 'KLAUTOANSWERS=/tmp/ans.txt /opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl'",
            "rm -f /tmp/ans.txt"
        ]
        results = run_ssh_commands(host, user, password, setup_cmds, dry_run=args.dry_run)

        if results is None: sys.exit(3)
        if all(r['status'] == 0 for r in results):
            logger.info("Instalação do KSC concluída com sucesso!")
            sys.exit(0)
        else:
            logger.error("Falha na instalação do KSC.")
            sys.exit(3)

    parser.print_help()

if __name__ == "__main__":
    main()
