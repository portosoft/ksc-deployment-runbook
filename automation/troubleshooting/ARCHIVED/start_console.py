import subprocess
import os
import sys


def start_console():
    # Environment variables
    env = os.environ.copy()
    env["FEATURE_MESSAGE_BROKER_TYPE"] = "nats"
    env["NATS_ADDRESS"] = "127.0.0.1"
    env["NATS_PORT"] = "4222"
    env["NSQ_HOST"] = "127.0.0.1"
    env["NSQ_PORT"] = "4222"

    # Working directory
    working_dir = "/var/opt/kaspersky/ksc-web-console"
    os.chdir(working_dir)

    # Command
    # We use ./node as it is the bundled version
    cmd = ["./node", "pm.js", "./pm.config.js"]

    print(f"Starting KSC Web Console from {working_dir}...")
    print(f"Command: {' '.join(cmd)}")

    try:
        # Run and stream output
        process = subprocess.Popen(
            cmd, env=env, stdout=sys.stdout, stderr=sys.stderr, universal_newlines=True
        )
        process.wait()
    except Exception as e:
        print(f"Error starting console: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start_console()
