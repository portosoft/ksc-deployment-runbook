import paramiko
import os
import sys
import time


def phase_0_debug_log_v5(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Kill stale processes
        print("--- Killing stale node processes ---")
        stdin, stdout, stderr = client.exec_command("sudo -S killall -9 node")
        stdin.write(password + "\n")
        stdin.flush()
        time.sleep(2)

        # Create a shell script on the server
        print("--- Creating remote debug script ---")
        # CD into directory before running node
        script_content = f"""#!/bin/bash
cd /var/opt/kaspersky/ksc-web-console
echo {password} | sudo -S ./node ./index.js > /tmp/ksc-console-debug.log 2>&1 &
"""
        client.exec_command(f"echo '{script_content}' > /tmp/run_debug.sh")
        client.exec_command("chmod +x /tmp/run_debug.sh")

        # Run it
        print("--- Executing remote debug script ---")
        client.exec_command("/tmp/run_debug.sh")

        print("Waiting 30 seconds for output...")
        time.sleep(30)

        print("--- 0.3 Output of /tmp/ksc-console-debug.log ---")
        stdin, stdout, stderr = client.exec_command("cat /tmp/ksc-console-debug.log")
        print(stdout.read().decode("utf-8"))

        # Check if it's running
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep node | grep index.js"
        )
        print("--- Running Node Process ---")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    phase_0_debug_log_v5(host, user, password)
