import paramiko
import os
import sys


def phase_1_audit(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 1.1 RPM Verify
        print("--- 1.1 RPM Verify ---")
        stdin, stdout, stderr = client.exec_command("rpm -V ksc-web-console")
        print(stdout.read().decode("utf-8"))

        # 1.2 RPM Info
        print("--- 1.2 RPM Info ---")
        stdin, stdout, stderr = client.exec_command("rpm -qi ksc-web-console")
        print(stdout.read().decode("utf-8"))

        # 1.4 Manually modified files
        print("--- 1.4 Manually modified files ---")
        # Reference point: the node binary (installed by RPM)
        cmd = 'sudo -S find /var/opt/kaspersky/ksc-web-console/server -newer /var/opt/kaspersky/ksc-web-console/node -name "*.js" 2>/dev/null'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # 1.5 PostgreSQL status
        print("--- 1.5 PostgreSQL Status ---")
        stdin, stdout, stderr = client.exec_command('sudo -u postgres psql -c "\\l"')
        print(stdout.read().decode("utf-8"))
        stdin, stdout, stderr = client.exec_command('sudo -u postgres psql -c "\\du"')
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    phase_1_audit(host, user, password)
