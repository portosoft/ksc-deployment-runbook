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

        remote_script = """
import re

with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

keywords = [
    b'ui_locales',
    b'resources_schedule_pkey',
    b'ksc_directory_object_uniq_idx',
    b'workspace_id',
    b'deleting_outbox'
]

# Function to extract printable SQL block around an offset
def get_sql_block(pos):
    # Walk backward to find non-printable characters or nulls
    start = pos
    while start > 0 and data[start] != 0 and (32 <= data[start] < 127 or data[start] in (10, 13)):
        start -= 1
    start += 1

    # Walk forward to find non-printable characters or nulls
    end = pos
    while end < len(data) and data[end] != 0 and (32 <= data[end] < 127 or data[end] in (10, 13)):
        end += 1

    return data[start:end].decode('ascii', errors='ignore')

for kw in keywords:
    print(f"\\n=================== KEYWORD: {kw.decode('ascii')} ===================")
    matches = list(re.finditer(kw, data))
    for m in matches:
        offset = m.start()
        block = get_sql_block(offset)
        if len(block) > 20:
            print(f"--- Block at offset {offset} ---")
            print(block)
            print("-" * 60)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/extract_sql_context.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command(
            "python3 /tmp/extract_sql_context.py"
        )
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/extract_sql_context.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
