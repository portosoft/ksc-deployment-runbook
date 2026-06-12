import paramiko
import os
import re
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Let's run a loop on the server itself via a shell script to make it very fast!
        # This shell script will test sections 1 to 150 for both SS_SETTINGS and SS_LOCAL_MACHINE
        shell_script = """
echo "=== Searching SS_SETTINGS ==="
for sec in {1..150}; do
    out=$(sudo LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/klscflag -ssvget -pv klserver -s $sec -ss '|ss_type = "SS_SETTINGS";' 2>/dev/null)
    if [ ! -z "$out" ]; then
        if echo "$out" | grep -q -i -E 'mfa|totp|2fa|two_factor|twofactor'; then
            echo "Found match in SS_SETTINGS section $sec:"
            echo "$out"
            echo "-----------------------------------"
        fi
    fi
done

echo "=== Searching SS_LOCAL_MACHINE ==="
for sec in {1..150}; do
    out=$(sudo LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/klscflag -ssvget -pv klserver -s $sec -ss '|ss_type = "SS_LOCAL_MACHINE";' 2>/dev/null)
    if [ ! -z "$out" ]; then
        if echo "$out" | grep -q -i -E 'mfa|totp|2fa|two_factor|twofactor'; then
            echo "Found match in SS_LOCAL_MACHINE section $sec:"
            echo "$out"
            echo "-----------------------------------"
        fi
    fi
done
"""
        stdin, stdout, stderr = client.exec_command("cat > /tmp/search_sections.sh")
        stdin.write(shell_script)
        stdin.close()
        stdout.read(); stderr.read()

        # Run the search script
        print("Running search script on remote server...")
        stdin, stdout, stderr = client.exec_command("bash /tmp/search_sections.sh")
        stdin.write(password + "\n")
        stdin.flush()

        print("--- Search Results ---")
        print(stdout.read().decode("utf-8", errors="replace"))

        client.exec_command("rm -f /tmp/search_sections.sh")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
