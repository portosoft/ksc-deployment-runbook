import paramiko
import os
import sys
import base64


def console_debug_logs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        target_file = (
            "/var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js"
        )

        # Read file
        stdin, stdout, stderr = client.exec_command(f"sudo -S cat {target_file}")
        stdin.write(password + "\n")
        stdin.flush()
        content = stdout.read().decode("utf-8")

        # Change runtime.logger to console.error
        content = content.replace("runtime.logger.error('DEBUG", "console.error('DEBUG")

        # Add debug to handleLoginRequest
        if "async handleLoginRequest(req, res) {" in content:
            content = content.replace(
                "async handleLoginRequest(req, res) {",
                "async handleLoginRequest(req, res) {\n        console.error('DEBUG: handleLoginRequest serversCount', this.serversCount);",
            )

        # Convert to base64
        b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        # Write back
        print("--- Writing file with console.error logs ---")
        client.exec_command(f"echo '{b64_content}' > /tmp/web-server-console.txt")
        client.exec_command(
            f"base64 -d /tmp/web-server-console.txt > /tmp/web-server-fixed.js"
        )
        stdin, stdout, stderr = client.exec_command(
            f"sudo -S cp /tmp/web-server-fixed.js {target_file}"
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

    console_debug_logs(host, user, password)
