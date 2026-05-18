import paramiko
import os
import sys
import json


def run_web_console_setup_v2(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=60)

        # Configuration JSON v2
        config = {
            "acceptEula": True,
            "address": "127.0.0.1",
            "port": 13299,
            "defaultLangId": 1046,
            "enableLog": True,
            "trusted": True,
            "certDomain": "***REMOVED***",
            "certPath": "",
            "keyPath": "",
            "additionalLocale": [],
            "installFolder": "/var/opt/kaspersky/ksc-web-console",
            "webConsoleAccount": {"user": "ksc", "group": "kladmins"},
            "serviceWebConsoleAccount": {"user": "ksc", "group": "kladmins"},
            "pluginAccount": {"user": "ksc", "group": "kladmins"},
            "managementServiceAccount": {"user": "ksc", "group": "kladmins"},
            "natsMessageQueueAccount": {"user": "ksc", "group": "kladmins"},
        }

        json_content = json.dumps(config, indent=2)

        # Upload JSON
        print("--- Uploading setup-v2.json ---")
        client.exec_command(f"echo '{json_content}' > /tmp/web-setup-v2.json")

        # Run Setup
        print("--- Running setup.js v2 ---")
        cmd = "cd /var/opt/kaspersky/ksc-web-console && sudo -S ./node setup.js /tmp/web-setup-v2.json"
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

    run_web_console_setup_v2(host, user, password)
