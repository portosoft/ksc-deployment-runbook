import paramiko
import os
import sys


def fix_debug_logs_syntax(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Fix syntax in web-server.js
        print("--- Fixing debug logs syntax in web-server.js ---")
        target_file = (
            "/var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js"
        )

        # Read file
        stdin, stdout, stderr = client.exec_command(f"sudo -S cat {target_file}")
        stdin.write(password + "\n")
        stdin.flush()
        content = stdout.read().decode("utf-8")

        # Replace broken logs with correct ones (using backticks or escaped quotes)
        broken_log1 = "runtime.logger.info(DEBUG: openAPIServers"
        fixed_log1 = "runtime.logger.info('DEBUG: openAPIServers'"
        broken_log2 = "runtime.logger.info(DEBUG: serversCount"
        fixed_log2 = "runtime.logger.info('DEBUG: serversCount'"

        if broken_log1 in content:
            new_content = content.replace(broken_log1, fixed_log1).replace(
                broken_log2, fixed_log2
            )

            # Write back
            client.exec_command(f"echo '{new_content}' > /tmp/web-server-fixed.js")
            stdin, stdout, stderr = client.exec_command(
                f"sudo -S cp /tmp/web-server-fixed.js {target_file}"
            )
            stdin.write(password + "\n")
            stdin.flush()

            # Restart
            print("--- Restarting ---")
            client.exec_command("sudo -S systemctl restart KSCWebConsole.service")
            stdin.write(password + "\n")
            stdin.flush()

            print("Done!")
        else:
            print("Broken log pattern not found!")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    fix_debug_logs_syntax(host, user, password)
