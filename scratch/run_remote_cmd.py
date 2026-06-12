import os
import sys
import paramiko
from dotenv import load_dotenv

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_remote_cmd.py <command>")
        sys.exit(1)

    cmd = " ".join(sys.argv[1:])
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    if not host or not user or not password:
        print("Error: Could not load KSC credentials.")
        sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password, timeout=30)

        use_sudo = "sudo" in cmd
        run_cmd = cmd.replace("sudo", "sudo -S", 1) if use_sudo else cmd

        stdin, stdout, stderr = client.exec_command(run_cmd)
        if use_sudo:
            stdin.write(password + "\n")
            stdin.flush()

        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")

        safe_out = out.encode("ascii", errors="replace").decode("ascii")
        safe_err = err.encode("ascii", errors="replace").decode("ascii")

        if safe_out:
            print("=== STDOUT ===")
            print(safe_out)
        if safe_err.strip():
            clean_err = safe_err.replace("[sudo] senha para suporte:", "").replace("[sudo] password for suporte:", "").strip()
            if clean_err:
                print("=== STDERR ===")
                print(clean_err)

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
