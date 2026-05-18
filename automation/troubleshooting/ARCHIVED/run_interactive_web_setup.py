import paramiko
import os
import sys
import time


def run_interactive_web_setup(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=60)

        print("--- Starting Interactive Web Console Setup ---")
        chan = client.get_transport().open_session()
        chan.get_pty()
        chan.settimeout(60)

        # Run node setup.js from its directory
        chan.exec_command(
            "cd /var/opt/kaspersky/ksc-web-console && sudo -S ./node setup.js"
        )

        # Send sudo password
        chan.send(password + "\n")
        time.sleep(2)

        # We need to capture the output and send answers
        # Typical answers: Y (EULA), Y (Privacy), etc.
        # I'll just capture 10 seconds of output to see the first question.

        output = ""
        for _ in range(20):
            if chan.recv_ready():
                output += chan.recv(4096).decode("utf-8")
            time.sleep(0.5)

        print(f"SETUP OUTPUT:\n{output}")

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    run_interactive_web_setup(host, user, password)
