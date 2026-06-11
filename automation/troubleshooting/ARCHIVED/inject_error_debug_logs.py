import paramiko
import os
import sys
import base64


def inject_error_debug_logs(host, user, password):
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

        # Change info to error for visibility
        content = content.replace(
            "runtime.logger.info('DEBUG", "runtime.logger.error('DEBUG"
        )

        # Convert to base64
        b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        # Write back
        print("--- Writing fixed file with error logs ---")
        client.exec_command(f"echo '{b64_content}' > /tmp/web-server-error.txt")
        client.exec_command(
            f"base64 -d /tmp/web-server-error.txt > /tmp/web-server-fixed.js"
        )
        stdin, stdout, stderr = client.exec_command(
            f"sudo -S cp /tmp/web-server-fixed.js {target_file}"
        )
        stdin.write(password + "\n")
        stdin.flush()

        # KILL ALL NODE and Restart
        print("--- Killing and Restarting ---")
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

    inject_error_debug_logs(host, user, password)
