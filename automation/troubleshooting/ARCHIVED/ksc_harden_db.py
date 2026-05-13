import os
import sys
import paramiko
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env local
load_dotenv(os.path.join(os.path.dirname(__file__), '../../configs/.env'))

def run_ssh_commands(host, user, password, commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    results = []
    try:
        client.connect(host, username=user, password=password, timeout=15)
        for cmd in commands:
            full_cmd = f"sudo -S {cmd}"
            stdin, stdout, stderr = client.exec_command(full_cmd)
            stdin.write(password + '\n')
            stdin.flush()

            res = {
                'command': cmd,
                'stdout': stdout.read().decode('utf-8'),
                'stderr': stderr.read().decode('utf-8'),
                'status': stdout.channel.recv_exit_status()
            }
            results.append(res)
        client.close()
    except Exception as e:
        print(f"Erro de Conexão: {e}")
        return None
    return results

def main():
    host = os.getenv('KSC_HOST')
    user = os.getenv('KSC_USER')
    password = os.getenv('KSC_PASS')

    if not all([host, user, password]):
        print("Erro: Variáveis de ambiente incompletas.")
        sys.exit(1)

    print(f"--- Aplicando Hardening do PostgreSQL para KSC em {host} ---")

    # Comandos baseados nas premissas validadas pelo usuário
    harden_cmds = [
        "sed -i \"s/^#max_connections = .*/max_connections = 200/\" /var/lib/pgsql/data/postgresql.conf",
        "grep -q 'escape_string_warning = on' /var/lib/pgsql/data/postgresql.conf || echo 'escape_string_warning = on' >> /var/lib/pgsql/data/postgresql.conf",
        "grep -q 'standard_conforming_strings = on' /var/lib/pgsql/data/postgresql.conf || echo 'standard_conforming_strings = on' >> /var/lib/pgsql/data/postgresql.conf",
        "systemctl restart postgresql.service",
        "sudo -u postgres psql -c \"ALTER USER kluser WITH PASSWORD 'REDACTED_DB_PASS';\"" # TODO: Parametrizar senha se necessário
    ]

    results = run_ssh_commands(host, user, password, harden_cmds)

    if results:
        for r in results:
            print(f"STATUS: {r['status']} | CMD: {r['command']}")
            if r['status'] != 0:
                print(f"ERRO: {r['stderr']}")

    print("\n--- Hardening Finalizado ---")

if __name__ == "__main__":
    main()
