import os
import re
import time
import sys
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    if not host or not user or not password:
        print("Error: Could not load KSC credentials.")
        sys.exit(1)

    print(f"Connecting to {user}@{host}...")
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password, timeout=30)
        print("Connected successfully.\n")

        # 4.1 Verificar o estado atual do kliam_srv em detalhe
        print("=== PASSO 4.1: Logs do kliam_srv (última hora, filtrado) ===")
        cmd_logs = 'sudo journalctl -u kliam_srv --since "1 hour ago" --no-pager | grep -iE "error|fatal|fail|migration|schema|database|connect"'
        run_cmd(client, password, cmd_logs)

        # 4.2 Verificar conectividade do kliam com o banco
        print("=== PASSO 4.2: Conectividade do kliam com o banco ===")
        cmd_conn = """sudo -u postgres psql -d ksciam -c "
SELECT datname, usename, application_name, state, query
FROM pg_stat_activity
WHERE datname = 'ksciam'
ORDER BY state;
" """
        run_cmd(client, password, cmd_conn)

        # 4.2.b Deletar registros de schema_migrations para forçar re-execução das migrações
        print("=== PASSO 4.2.b: Deletando registros da tabela public.schema_migrations ===")
        cmd_delete = 'sudo -u postgres psql -d ksciam -c "DELETE FROM public.schema_migrations;"'
        run_cmd(client, password, cmd_delete)

        # 4.3 Forçar restart do kliam_srv para disparar migração
        print("=== PASSO 4.3: Reiniciar kliam_srv ===")
        cmd_restart = "sudo systemctl restart kliam_srv"
        run_cmd(client, password, cmd_restart)

        print("Aguardando 45 segundos para que as migrações sejam aplicadas...")
        time.sleep(45)

        # 4.4 Verificar novamente a contagem de tabelas
        print("=== PASSO 4.4: Contagem de tabelas no ksciam (Tentativa 1) ===")
        cmd_tables = """sudo -u postgres psql -d ksciam -c "
SELECT table_schema, COUNT(*) AS total_tabelas
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('pg_catalog', 'information_schema')
GROUP BY table_schema
ORDER BY table_schema;
" """
        out_tables, _ = run_cmd(client, password, cmd_tables)

        # Let's check the table count for 'iam' schema from stdout
        # Sample output:
        #  iam          |            17
        iam_count = get_iam_table_count(out_tables)
        print(f"Número de tabelas no esquema 'iam': {iam_count}")

        if iam_count < 40:
            print("Número de tabelas ainda é menor que 40. Aguardando mais 60 segundos (Tentativa 2)...")
            time.sleep(60)
            print("=== PASSO 4.4: Contagem de tabelas no ksciam (Tentativa 2) ===")
            out_tables, _ = run_cmd(client, password, cmd_tables)
            iam_count = get_iam_table_count(out_tables)
            print(f"Número de tabelas no esquema 'iam' (Tentativa 2): {iam_count}")

        # 4.5 Verificar status do kliam após restart
        print("=== PASSO 4.5: Status e logs recentes do kliam_srv ===")
        run_cmd(client, password, "systemctl status kliam_srv --no-pager -l")
        run_cmd(client, password, "sudo journalctl -u kliam_srv -n 30 --no-pager")

        client.close()
    except Exception as e:
        print(f"An error occurred: {e}")

def run_cmd(client, password, cmd):
    use_sudo = "sudo" in cmd
    run_cmd = cmd.replace("sudo", "sudo -S", 1) if use_sudo else cmd

    stdin, stdout, stderr = client.exec_command(run_cmd)
    if use_sudo:
        stdin.write(password + "\n")
        stdin.flush()

    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")

    # Safe print for Windows console
    safe_out = out.encode("ascii", errors="replace").decode("ascii")
    safe_err = err.encode("ascii", errors="replace").decode("ascii")

    print("STDOUT:")
    print(safe_out)
    if safe_err.strip():
        clean_err = safe_err.replace("[sudo] senha para suporte:", "").replace("[sudo] password for suporte:", "").strip()
        if clean_err:
            print("STDERR:")
            print(clean_err)
    print("-" * 60 + "\n")
    return out, err

def get_iam_table_count(stdout_str):
    # Regex to find 'iam | <number>' or 'iam |  <number>'
    match = re.search(r'iam\s*\|\s*(\d+)', stdout_str)
    if match:
        return int(match.group(1))
    return 0

if __name__ == "__main__":
    main()
