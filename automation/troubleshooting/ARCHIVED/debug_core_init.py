import paramiko
import os
import sys
import base64


def debug_core_init(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 1. Inject into server/core/server.js (Base class constructor)
        print("--- Injecting into server/core/server.js ---")
        base_file = "/var/opt/kaspersky/ksc-web-console/server/core/server.js"
        stdin, stdout, stderr = client.exec_command(f"sudo -S cat {base_file}")
        stdin.write(password + "\n")
        stdin.flush()
        base_content = stdout.read().decode("utf-8")

        if "constructor({" in base_content:
            base_content = base_content.replace(
                "constructor({",
                "constructor({\n        console.error('DEBUG: BusinessLogicServer base constructor called');",
            )

        b64_base = base64.b64encode(base_content.encode("utf-8")).decode("utf-8")
        client.exec_command(f"echo '{b64_base}' > /tmp/server-base.txt")
        client.exec_command(f"base64 -d /tmp/server-base.txt > /tmp/server-base.js")
        stdin, stdout, stderr = client.exec_command(
            f"sudo -S cp /tmp/server-base.js {base_file}"
        )
        stdin.write(password + "\n")
        stdin.flush()

        # 2. Inject into server/core/env-local/web-server.js
        print("--- Injecting into server/core/env-local/web-server.js ---")
        local_file = (
            "/var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js"
        )
        stdin, stdout, stderr = client.exec_command(f"sudo -S cat {local_file}")
        stdin.write(password + "\n")
        stdin.flush()
        local_content = stdout.read().decode("utf-8")

        if "constructor() {" in local_content:
            local_content = local_content.replace(
                "constructor() {",
                "constructor() {\n        super();\n        console.error('DEBUG: WebServer env-local constructor called');\n        console.error('DEBUG: global.config.openAPIServers', JSON.stringify(global.config.openAPIServers));",
            )
            # Remove the double super() if it was there
            local_content = local_content.replace(
                "super();\n        super();", "super();"
            )

        b64_local = base64.b64encode(local_content.encode("utf-8")).decode("utf-8")
        client.exec_command(f"echo '{b64_local}' > /tmp/web-server-local.txt")
        client.exec_command(
            f"base64 -d /tmp/web-server-local.txt > /tmp/web-server-local.js"
        )
        stdin, stdout, stderr = client.exec_command(
            f"sudo -S cp /tmp/web-server-local.js {local_file}"
        )
        stdin.write(password + "\n")
        stdin.flush()

        # KILL and RESTART
        print("--- Restarting ---")
        client.exec_command("sudo -S killall -9 node")
        client.exec_command("sudo -S systemctl restart KSCWebConsole.service")
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

    debug_core_init(host, user, password)
