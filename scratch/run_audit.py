import os
import sys
import paramiko
from dotenv import load_dotenv

def upload_dir(sftp, local_dir, remote_dir):
    try:
        sftp.mkdir(remote_dir)
    except IOError:
        pass
    for item in os.listdir(local_dir):
        if item == "__pycache__": continue
        local_path = os.path.join(local_dir, item)
        remote_path = f"{remote_dir}/{item}"
        if os.path.isfile(local_path):
            sftp.put(local_path, remote_path)
        elif os.path.isdir(local_path):
            upload_dir(sftp, local_path, remote_path)

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    client.connect(host, username=user, password=password)

    print("Uploading automation/python module...")
    sftp = client.open_sftp()

    # We need to upload configs as well because ksc_audit depends on configs/env/ksc_vars.env
    try: sftp.mkdir("/tmp/ksc_runbook")
    except: pass
    try: sftp.mkdir("/tmp/ksc_runbook/automation")
    except: pass
    try: sftp.mkdir("/tmp/ksc_runbook/configs")
    except: pass
    try: sftp.mkdir("/tmp/ksc_runbook/configs/env")
    except: pass

    sftp.put("configs/env/ksc_vars.env", "/tmp/ksc_runbook/configs/env/ksc_vars.env")
    upload_dir(sftp, "automation/python", "/tmp/ksc_runbook/automation/python")
    sftp.close()

    print("Running ksc_audit on remote host...")
    cmd = "cd /tmp/ksc_runbook && python3 -m automation.python.ksc_audit --postcheck"
    stdin, stdout, stderr = client.exec_command(cmd)

    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    status = stdout.channel.recv_exit_status()

    if out: print(f"[STDOUT]\n{out}")
    if err: print(f"[STDERR]\n{err}")
    print(f"[EXIT STATUS] {status}")

    client.close()
    if status != 0: sys.exit(1)

if __name__ == "__main__":
    main()
