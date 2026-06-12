import os
import sys
import paramiko
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env local
load_dotenv(os.path.join(os.path.dirname(__file__), "../../configs/.env"))


def run_ssh_commands(host, user, password, commands):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    results = []
    try:
        client.connect(host, username=user, password=password, timeout=15)
        for cmd_dict in commands:
            cmd = cmd_dict['cmd']
            cmd_stdin = cmd_dict.get('stdin', '')
            full_cmd = f"sudo -S {cmd}"
            stdin, stdout, stderr = client.exec_command(full_cmd)
            # Write sudo password
            stdin.write(password + "\n")
            # Write any additional stdin payload securely
            if cmd_stdin:
                stdin.write(cmd_stdin + "\n")
            stdin.flush()
            # Close stdin so commands like psql reading from it know we are done
            stdin.channel.shutdown_write()

            res = {
                "command": cmd,
                "stdout": stdout.read().decode("utf-8"),
                "stderr": stderr.read().decode("utf-8"),
                "status": stdout.channel.recv_exit_status(),
            }
            results.append(res)
        client.close()
    except Exception as e:
        print(f"Erro de Conexão: SSH connection failed.")
        return None
    return results


def main():
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    db_password = os.getenv("KSC_DB_PASS")

    if not all([host, user, password, db_password]):
        print("Erro: Variáveis de ambiente incompletas.")
        sys.exit(1)

    print("--- Aplicando Hardening do PostgreSQL para KSC ---")

    # Comandos baseados nas premissas validadas pelo usuário
    harden_cmds = [
        {'cmd': 'sed -i "s/^#max_connections = .*/max_connections = 200/" /var/lib/pgsql/data/postgresql.conf'},
        {'cmd': "grep -q 'escape_string_warning = on' /var/lib/pgsql/data/postgresql.conf || echo 'escape_string_warning = on' >> /var/lib/pgsql/data/postgresql.conf"},
        {'cmd': "grep -q 'standard_conforming_strings = on' /var/lib/pgsql/data/postgresql.conf || echo 'standard_conforming_strings = on' >> /var/lib/pgsql/data/postgresql.conf"},
        {'cmd': "systemctl restart postgresql.service"},
    ]

    results = run_ssh_commands(host, user, password, harden_cmds)

    if results:
        for r in results:
            print(f"STATUS: {r['status']} | CMD: {r['command']}")
            if r["status"] != 0:
                print(f"ERRO: [Command failed]")

    # Executar a alteração de senha de forma segura e separada
    print("--- Atualizando senha do banco de dados (postgres) ---")
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=15)
        stdin, stdout, stderr = client.exec_command("sudo -S sudo -u postgres psql")
        stdin.write(password + "\n")
        stdin.flush()
        stdin.write(f"ALTER USER kluser WITH PASSWORD '{db_password}';\n")
        stdin.flush()
        stdin.channel.shutdown_write()
        status = stdout.channel.recv_exit_status()
        if status == 0:
            print("Senha do banco de dados atualizada com sucesso.")
        else:
            print("Erro ao atualizar a senha do banco de dados.")
        client.close()
    except Exception:
        print("Erro ao conectar para atualizar a senha do banco de dados.")

    print("\n--- Hardening Finalizado ---")


if __name__ == "__main__":
    main()
