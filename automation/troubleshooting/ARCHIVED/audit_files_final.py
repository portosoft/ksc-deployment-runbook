import paramiko
import os
import sys


def audit_files_final(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        files = [
            "/var/opt/kaspersky/ksc-web-console/server/index.js",
            "/var/opt/kaspersky/ksc-web-console/server/core/server.js",
            "/var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js",
        ]

        print("--- MD5SUM of target files ---")
        for f in files:
            stdin, stdout, stderr = client.exec_command(f"md5sum {f}")
            print(stdout.read().decode("utf-8").strip())

        print("\n--- RPM Verify of target files ---")
        for f in files:
            stdin, stdout, stderr = client.exec_command(
                f'rpm -V ksc-web-console | grep "{f}"'
            )
            out = stdout.read().decode("utf-8").strip()
            if out:
                print(out)
            else:
                print(f"{f}: OK (according to RPM)")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    audit_files_final(host, user, password)
