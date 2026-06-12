import os
import sys
import paramiko
from dotenv import load_dotenv


def get_credentials():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    if not host or not user or not password:
        print("Error: Could not load KSC credentials from configs/env/ksc_vars.env")
        sys.exit(1)

    return host, user, password


def connect_ssh(host, user, password):
    print(f"Connecting to {user}@{host}...")
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host, username=user, password=password, timeout=30)
    print("Connected successfully.\n")
    return client


def get_diagnostic_commands():
    return [
        # 1.1 Estado dos serviços systemd
        ("1.1.1", "systemctl status kladminserver_srv --no-pager -l"),
        ("1.1.2", "systemctl status kliam_srv --no-pager -l"),
        ("1.1.3", "systemctl status ksc-web-console --no-pager -l"),
        ("1.1.4", "systemctl status postgresql --no-pager -l"),
        # 1.2 Verificação de portas em escuta (run with sudo to see process owners)
        ("1.2", "sudo ss -tlnp | grep -E '13000|13299|8080|5432|9500|4222'"),
        # 1.3 Verificação do arquivo de configuração do Web Console
        ("1.3", "sudo cat /var/opt/kaspersky/ksc-web-console/server/config.json"),
        # 1.4 Verificação do JSON de setup persistido
        ("1.4", "sudo cat /etc/ksc-web-console-setup.json"),
        # 1.5 Verificação dos certificados referenciados
        ("1.5.1", "sudo ls -la /var/opt/kaspersky/ksc-web-console/KLRootCA.crt"),
        ("1.5.2", "sudo ls -la /var/opt/kaspersky/klnagent_srv/1093/cert/klserver.cer"),
        ("1.5.3", "sudo ls -la /var/opt/kaspersky/klnagent_srv/1093/cert/klsrvJWEsign.cer"),
        ("1.5.4", "sudo ls -la /var/opt/kaspersky/klnagent_srv/1093/iam/klsrvJWEsign.prk"),
        ("1.5.5", "sudo ls -la /var/opt/kaspersky/klnagent_srv/1093/iam/klsrvJWEencrypt.cer"),
        # 1.6 Verificação do iam_config.yaml
        ("1.6", "sudo cat /var/opt/kaspersky/klnagent_srv/iam/iam_config.yaml"),
        # 1.7 Auditoria do banco ksciam
        (
            "1.7",
            """sudo -u postgres psql -d ksciam -c "
SELECT table_schema, COUNT(*) AS total_tabelas
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('pg_catalog', 'information_schema')
GROUP BY table_schema
ORDER BY table_schema;
" """,
        ),
        # 1.8 Verificação da tabela de usuários IAM
        (
            "1.8",
            'sudo -u postgres psql -d ksciam -c "SELECT name, id FROM iam.users;"',
        ),
        # 1.9 Verificação do usuário no banco ksc
        (
            "1.9",
            """sudo -u postgres psql -d ksc -c "
SELECT \\\"wstrName\\\", \\\"binId\\\"
FROM spl_users
WHERE \\\"wstrName\\\" IN ('kscadmin', 'KLAdmins', 'kscadmin2');
" """,
        ),
        # 1.10 Verificação das exceções de MFA
        (
            "1.10.1",
            'sudo -u postgres psql -d ksc -c "SELECT * FROM mfa_totp_exceptions;"',
        ),
        (
            "1.10.2",
            'sudo -u postgres psql -d ksc -c "SELECT * FROM mfa_totp_settings;"',
        ),
        # 1.11 Teste direto da API OpenAPI (can run as normal user from server)
        (
            "1.11",
            """curl -k -s -o /dev/null -w "%{http_code}" -X POST https://127.0.0.1:13299/api/v1.0/login -H "Content-Type: application/json" -d '{}'""",
        ),
        # 1.12 Verificação da flag OpenAPI no klscflag
        (
            "1.12",
            """sudo LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/klscflag -ssvget -pv klserver -s 87 -n KLSRV_SP_OPEN_OAPI_PORT -ss '|ss_type = "SS_SETTINGS";'""",
        ),
        # 1.13 Últimas 50 linhas de log de cada serviço
        ("1.13.1", "sudo journalctl -u kladminserver_srv -n 50 --no-pager"),
        ("1.13.2", "sudo journalctl -u kliam_srv -n 50 --no-pager"),
        ("1.13.3", "sudo journalctl -u ksc-web-console -n 50 --no-pager"),
    ]


def execute_commands_and_save(client, commands, password, output_filepath):
    with open(output_filepath, "w", encoding="utf-8") as outfile:
        for step, cmd in commands:
            outfile.write(f"=== PASSO {step} ===\n")
            outfile.write(f"Comando: {cmd}\n")

            # Execute command. If it needs sudo, inject the password.
            use_sudo = "sudo" in cmd
            if use_sudo:
                run_cmd = cmd.replace("sudo", "sudo -S", 1)
            else:
                run_cmd = cmd

            stdin, stdout, stderr = client.exec_command(run_cmd)

            if use_sudo:
                stdin.write(password + "\n")
                stdin.flush()
                stdin.channel.shutdown_write()

            out = stdout.read().decode("utf-8", errors="replace")
            err = stderr.read().decode("utf-8", errors="replace")

            # Safe write
            outfile.write("--- STDOUT ---\n")
            outfile.write(out)
            if err.strip():
                # Strip out sudo password prompt if it exists
                clean_err = (
                    err.replace("[sudo] senha para suporte:", "")
                    .replace("[sudo] password for suporte:", "")
                    .strip()
                )
                if clean_err:
                    outfile.write("--- STDERR ---\n")
                    outfile.write(clean_err + "\n")
            outfile.write("=" * 80 + "\n\n")

    print(f"Diagnostics complete. Raw output saved to: {output_filepath}")


def main():
    host, user, password = get_credentials()

    try:
        client = connect_ssh(host, user, password)
        commands = get_diagnostic_commands()
        output_filepath = "scratch/post_remediation_raw_output.txt"
        execute_commands_and_save(client, commands, password, output_filepath)
        client.close()
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
