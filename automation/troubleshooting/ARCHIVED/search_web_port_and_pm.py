import paramiko
import os
import sys


def search_web_port_and_pm(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for 8080 or other common ports
        print("--- Searching for ports in configs ---")
        cmd = "grep -rE '8080|443|8443' /var/opt/kaspersky/ksc-web-console/server/config.json /var/opt/kaspersky/ksc-web-console/*.js 2>/dev/null | head -n 20"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        # Read pm.service-console.js
        print("--- Reading pm.service-console.js ---")
        stdin, stdout, stderr = client.exec_command(
            "head -n 50 /var/opt/kaspersky/ksc-web-console/pm.service-console.js"
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    search_web_port_and_pm(host, user, password)
