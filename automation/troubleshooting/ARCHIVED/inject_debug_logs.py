import paramiko
import os
import sys


def inject_debug_logs(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Inject log into web-server.js constructor
        print("--- Injecting debug logs into web-server.js ---")
        target_file = (
            "/var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js"
        )

        # Read file
        stdin, stdout, stderr = client.exec_command(f"sudo -S cat {target_file}")
        stdin.write(password + "\n")
        stdin.flush()
        content = stdout.read().decode("utf-8")

        # Add log in constructor
        debug_log = "\n        runtime.logger.info('DEBUG: openAPIServers', JSON.stringify(global.config.openAPIServers));\n        runtime.logger.info('DEBUG: serversCount', this.serversCount);"
        if "this.serversCount = 0;" in content:
            new_content = content.replace(
                "this.serversCount = 0;", "this.serversCount = 0;" + debug_log
            )

            # Write back
            client.exec_command(f"echo '{new_content}' > /tmp/web-server-debug.js")
            stdin, stdout, stderr = client.exec_command(
                f"sudo -S cp /tmp/web-server-debug.js {target_file}"
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
            print("Could not find insertion point!")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    inject_debug_logs(host, user, password)
