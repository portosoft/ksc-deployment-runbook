import paramiko
import os
import sys
import time

def phase_0_debug_log(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 0.2 Check logs with sudo
        print("--- 0.2 Log Files (Internal) with sudo ---")
        stdin, stdout, stderr = client.exec_command('sudo -S find /var/opt/kaspersky/ksc-web-console -name "*.log" -type f 2>/dev/null | head -20')
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        # 0.3 Stop service and run node manually
        print("--- 0.3 Redirecting output to /tmp/ksc-console-debug.log ---")
        client.exec_command('sudo -S systemctl stop KSCWebConsole.service')

        # Run node in background
        # Note: I need to use index.js as found in previous steps
        cmd = 'sudo -S /var/opt/kaspersky/ksc-web-console/node/bin/node /var/opt/kaspersky/ksc-web-console/index.js > /tmp/ksc-console-debug.log 2>&1 &'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + '\n')
        stdin.flush()

        print("Waiting 15 seconds for output...")
        time.sleep(15)

        print("--- 0.3 Output of /tmp/ksc-console-debug.log ---")
        stdin, stdout, stderr = client.exec_command('cat /tmp/ksc-console-debug.log')
        print(stdout.read().decode('utf-8'))

        # Also check if it's still running
        stdin, stdout, stderr = client.exec_command('ps aux | grep node | grep index.js')
        print("--- Running Node Process ---")
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    phase_0_debug_log(host, user, password)
