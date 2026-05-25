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
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        remote_script = """
import re

with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

# Let's search for keywords like 'CREATE TABLE', 'CREATE VIEW', 'CREATE SCHEMA'
# and extract contiguous printable ASCII/UTF-8 blocks.
patterns = [
    rb'CREATE\s+TABLE\s+[a-zA-Z0-9_.]+',
    rb'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+[a-zA-Z0-9_.]+',
    rb'CREATE\s+SCHEMA',
    rb'ALTER\s+TABLE\s+[a-zA-Z0-9_.]+'
]

seen_offsets = set()

for pat in patterns:
    for match in re.finditer(pat, data, re.IGNORECASE):
        start = match.start()
        # Find the block start (e.g. walk back to a newline or BEGIN or semicolon or null)
        block_start = start
        while block_start > 0 and data[block_start] != 0 and (32 <= data[block_start] < 127 or data[block_start] in (10, 13)):
            block_start -= 1
        block_start += 1
        
        # Find the block end (walk forward to a null or non-printable char)
        block_end = start
        while block_end < len(data) and data[block_end] != 0 and (32 <= data[block_end] < 127 or data[block_end] in (10, 13)):
            block_end += 1
            
        if block_start in seen_offsets:
            continue
        seen_offsets.add(block_start)
        
        chunk = data[block_start:block_end]
        # Only print if it looks like a real SQL chunk (contains SELECT, CREATE, or ALTER and is long enough)
        if len(chunk) > 30:
            printable = chunk.decode('ascii', errors='ignore')
            print(f"=== SQL Block at offset {block_start} (len {len(chunk)}) ===")
            print(printable)
            print("="*60)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/find_sql_in_binary.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/find_sql_in_binary.py")
        print(stdout.read().decode("utf-8", errors="replace"))

        client.exec_command("rm -f /tmp/find_sql_in_binary.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
