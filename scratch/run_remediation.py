import os
import sys
import time
import paramiko
from dotenv import load_dotenv

def run_cmd(client, cmd, password=None, use_sudo=False, print_output=True, abort_on_fail=False):
    if use_sudo:
        cmd = cmd.replace("sudo ", "sudo -S ", 1)
        if not cmd.startswith("sudo"):
            cmd = "sudo -S " + cmd

    print(f"\n[EXEC] {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)

    if use_sudo and password:
        stdin.write(password + "\n")
        stdin.flush()

    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8').strip()
    err = stderr.read().decode('utf-8').strip()

    if err and "[sudo] password for" in err:
        # filter out the password prompt
        lines = err.split('\n')
        err = '\n'.join([line for line in lines if "[sudo] password for" not in line and "[sudo] senha para" not in line])
        err = err.strip()

    if print_output:
        if out: print(f"[STDOUT]\n{out}")
        if err: print(f"[STDERR]\n{err}")
        print(f"[EXIT STATUS] {exit_status}")

    if abort_on_fail and exit_status != 0:
        print(f"\n[CRITICAL FAILURE] Command failed with status {exit_status}. Aborting.")
        sys.exit(1)

    return exit_status, out, err

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    fqdn = os.getenv("KSC_FQDN", host)
    admin_user = os.getenv("KSC_ADMIN_USER", "KLAdmins")
    admin_pass = os.getenv("KSC_ADMIN_PASS")

    if not all([host, user, password]):
        print("Missing required env vars.")
        sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    print(f"Connecting to {user}@{host}...")
    client.connect(host, username=user, password=password)
    print("Connected.")

    print("\n" + "="*50 + "\nPASSO 1 — Certificado SSL\n" + "="*50)
    run_cmd(client, "cp /var/opt/kaspersky/ksc-web-console/KLRootCA.crt /etc/pki/ca-trust/source/anchors/ksc-webconsole-ca.crt", password, use_sudo=True, abort_on_fail=True)
    run_cmd(client, "update-ca-trust extract", password, use_sudo=True, abort_on_fail=True)

    _, out, _ = run_cmd(client, "openssl verify -CAfile /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem /var/opt/kaspersky/ksc-web-console/KLRootCA.crt", password, use_sudo=True)
    if "OK" not in out:
        print("Validation failed. Not OK.")
        sys.exit(1)

    run_cmd(client, "cp /var/opt/kaspersky/ksc-web-console/KLRootCA.crt /tmp/ksc-ca-for-browser.crt", password, use_sudo=True, abort_on_fail=True)

    print("\n" + "="*50 + "\nPASSO 2 — Validar Porta\n" + "="*50)
    _, out_ss, _ = run_cmd(client, "ss -tlnp | grep -E '8080|8443|443'", password, use_sudo=True)
    run_cmd(client, "systemctl status ksc-web-console | grep -i port", password, use_sudo=False)

    status, fw_out, _ = run_cmd(client, "firewall-cmd --list-ports | grep -E '8080|8443|443'", password, use_sudo=True)
    if "8080" not in fw_out and "8443" not in fw_out and "443" not in fw_out:
        run_cmd(client, "firewall-cmd --permanent --add-port=8080/tcp && sudo -S firewall-cmd --reload", password, use_sudo=True, abort_on_fail=True)

    print("\n" + "="*50 + "\nPASSO 3 — Reconfigurar config.json\n" + "="*50)
    setup_json = f"""{{
  "acceptEula": true,
  "address": "",
  "port": 8080,
  "defaultLanguageId": "pt-BR",
  "trusted": {{
    "": {{
      "kscHost": "127.0.0.1",
      "kscPort": 13299,
      "kscCertPath": "/var/opt/kaspersky/ksc-web-console/KLRootCA.crt"
    }}
  }}
}}"""
    sftp = client.open_sftp()
    with sftp.file("/tmp/ksc-setup-fix.json", "w") as f:
        f.write(setup_json)
    sftp.close()

    run_cmd(client, "bash -c 'cd /var/opt/kaspersky/ksc-web-console && ./node setup.js /tmp/ksc-setup-fix.json'", password, use_sudo=True, abort_on_fail=True)

    py_check = """python3 -c "
import json
with open('/var/opt/kaspersky/ksc-web-console/server/config.json') as f:
  c = json.load(f)
pools = c.get('openAPIServers', {}).get('pools', [])
servers = pools[0].get('servers', []) if pools else []
print('ERRO: lista de servidores vazia') if not servers else print(f'OK: {len(servers)} servidor(es) configurado(s)')
" """
    _, out_py, _ = run_cmd(client, py_check, password, use_sudo=True)
    if "ERRO" in out_py:
        print("Config.json failed verification!")
        sys.exit(1)

    run_cmd(client, "cp /tmp/ksc-setup-fix.json /etc/ksc-web-console-setup.json", password, use_sudo=True, abort_on_fail=True)

    print("\n" + "="*50 + "\nPASSO 4 — Habilitar OpenAPI 13299\n" + "="*50)
    status, out_oapi, _ = run_cmd(client, "ss -tlnp | grep 13299", password, use_sudo=True)
    if status != 0:
        klscflag_cmd = "LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/klscflag -ssvset -pv klserver -s 87 -n KLSRV_SP_OPEN_OAPI_PORT -sv true -svt BOOL_T -ss '|ss_type = \"SS_SETTINGS\";'"
        run_cmd(client, klscflag_cmd, password, use_sudo=True, abort_on_fail=True)
        run_cmd(client, "systemctl restart kladminserver_srv", password, use_sudo=True, abort_on_fail=True)
        run_cmd(client, "ss -tlnp | grep 13299", password, use_sudo=True, abort_on_fail=True)

    print("\n" + "="*50 + "\nPASSO 5 — Validar serviços e reiniciar\n" + "="*50)
    run_cmd(client, "systemctl stop ksc-web-console kliam_srv kladminserver_srv", password, use_sudo=True, abort_on_fail=True)

    status, ld_out, _ = run_cmd(client, "systemctl cat kladminserver_srv | grep LD_LIBRARY", password, use_sudo=False)
    if status != 0:
        run_cmd(client, "mkdir -p /etc/systemd/system/kladminserver_srv.service.d/", password, use_sudo=True)
        run_cmd(client, "bash -c 'echo -e \"[Service]\\nEnvironment=LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib\" > /etc/systemd/system/kladminserver_srv.service.d/ldpath.conf'", password, use_sudo=True)
        run_cmd(client, "systemctl daemon-reload", password, use_sudo=True, abort_on_fail=True)

    run_cmd(client, "systemctl start kladminserver_srv", password, use_sudo=True, abort_on_fail=True)
    print("Sleeping 30s...")
    time.sleep(30)
    run_cmd(client, "systemctl start kliam_srv", password, use_sudo=True, abort_on_fail=True)
    print("Sleeping 15s...")
    time.sleep(15)
    run_cmd(client, "systemctl start ksc-web-console", password, use_sudo=True, abort_on_fail=True)

    run_cmd(client, "for svc in kladminserver_srv kliam_srv ksc-web-console; do echo \"=== $svc ===\"; systemctl is-active $svc; done", password, use_sudo=False)

    print("\n" + "="*50 + "\nPASSO 6 — Teste de API\n" + "="*50)
    api_cmd = f"""ADMIN_PASS_B64=$(echo -n "{admin_pass}" | base64)
ADMIN_USER_B64=$(echo -n "{admin_user}" | base64)
curl -sk -o /dev/null -w "%{{http_code}}" \\
  -X POST https://127.0.0.1:13299/api/v1.0/login \\
  -H "Content-Type: application/json" \\
  -H "Authorization: KSCBasic user=\\"$ADMIN_USER_B64\\", pass=\\"$ADMIN_PASS_B64\\", internal=\\"1\\""
"""
    _, out_api, _ = run_cmd(client, api_cmd, password, use_sudo=False)
    if out_api.strip() == "401":
        print("API test returned 401. User must take action (e.g., purge MFA or check password).")
    elif out_api.strip() == "200":
        print("API test SUCCESS (200)!")
    else:
        print(f"API test returned unexpected status: {out_api}")

    client.close()
    print("\nDONE!")

if __name__ == "__main__":
    main()
