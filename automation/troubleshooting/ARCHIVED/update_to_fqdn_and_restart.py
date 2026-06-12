import paramiko
import os
import sys
import json
import uuid


def update_to_fqdn_and_restart(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 1. Read existing config.json
        print("--- Reading current config.json ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cat /var/opt/kaspersky/ksc-web-console/server/config.json"
        )
        stdin.write(password + "\n")
        stdin.flush()
        config_content = stdout.read().decode("utf-8")

        # Strip sudo prompt if present
        if "[sudo]" in config_content:
            config_content = config_content.split("\n", 1)[1]

        config = json.loads(config_content)

        # 2. Update address to FQDN
        print("--- Updating address to FQDN ---")
        fqdn = "***REMOVED***"
        if config["openAPIServers"]["pools"][0]["servers"]:
            config["openAPIServers"]["pools"][0]["servers"][0]["address"] = fqdn

        new_config_json = json.dumps(config, indent=2)

        # 3. Write new config.json
        print("--- Writing updated config.json ---")
        client.exec_command(f"echo '{new_config_json}' > /tmp/config_fqdn.json")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cp /tmp/config_fqdn.json /var/opt/kaspersky/ksc-web-console/server/config.json"
        )
        stdin.write(password + "\n")
        stdin.flush()

        # 4. Deep Restart
        print("--- Deep Restarting Services ---")
        client.exec_command(
            "sudo -S systemctl stop KSCWebConsole.service KSCSvcWebConsole.service"
        )
        client.exec_command("sudo -S killall -9 node")
        import time

        time.sleep(2)
        client.exec_command(
            "sudo -S systemctl start KSCSvcWebConsole.service KSCWebConsole.service"
        )
        stdin.write(password + "\n")
        stdin.flush()

        print("Done!")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    update_to_fqdn_and_restart(host, user, password)
