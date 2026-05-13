import sys
import os
import paramiko

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import vault

def run_ssh(host, user, password, commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=30)

    secrets = vault.decrypt_secrets()
    sensitive_vals = [str(v) for v in secrets.values()]

    for cmd in commands:
        masked_cmd = cmd
        for val in sensitive_vals:
            if val and len(val) > 3:
                masked_cmd = masked_cmd.replace(val, '***REMOVED***')
        print(f"Executing: {masked_cmd}")
        # Run with timeout to capture output and then kill it
        full_cmd = f"timeout 30s sudo -S {cmd}"
        stdin, stdout, stderr = client.exec_command(full_cmd)
        stdin.write(password + '\n')
        stdin.flush()
        out = stdout.read().decode('utf-8', errors='ignore')
        err = stderr.read().decode('utf-8', errors='ignore')
        if out: print(out.encode('ascii', 'backslashreplace').decode('ascii'))
        if err and "sudo: a senha" not in err: print(err.encode('ascii', 'backslashreplace').decode('ascii'))
    client.close()

secrets = vault.decrypt_secrets()

cmds = [
    "systemctl stop ksc-web-console || true",
    "bash -c 'cd /var/opt/kaspersky/ksc-web-console && ./node index.js'"
]

run_ssh(secrets['KSC_HOST'], secrets['KSC_USER'], secrets['KSC_PASS'], cmds)
