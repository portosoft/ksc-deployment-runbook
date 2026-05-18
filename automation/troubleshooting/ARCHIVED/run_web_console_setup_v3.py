import paramiko
import os
import sys
import json


def run_web_console_setup_v3(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=60)

        # Configuration JSON v3
        config = {
            "acceptEula": True,
            "address": "127.0.0.1",
            "port": "13299",
            "defaultLangId": 1046,
            "enableLog": True,
            "trusted": True,
            "certDomain": "***REMOVED***",
            "certPath": "",
            "keyPath": "",
            "additionalLocale": "",
            "installFolder": "/var/opt/kaspersky/ksc-web-console",
            "webConsoleAccount": "ksc:kladmins",
            "serviceWebConsoleAccount": "ksc:kladmins",
            "pluginAccount": "ksc:kladmins",
            "managementServiceAccount": "ksc:kladmins",
            "natsMessageQueueAccount": "ksc:kladmins",
        }

        json_content = json.dumps(config, indent=2)

        # Upload JSON
        print("--- Uploading setup-v3.json ---")
        client.exec_command(f"echo '{json_content}' > /tmp/web-setup-v3.json")

        # Run Setup
        print("--- Running setup.js v3 ---")
        cmd = "cd /var/opt/kaspersky/ksc-web-console && sudo -S ./node setup.js /tmp/web-setup-v3.json"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()

        print(f"STDOUT:\n{stdout.read().decode('utf-8')}")
        print(f"STDERR:\n{stderr.read().decode('utf-8')}")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    run_web_console_setup_v3(host, user, password)
