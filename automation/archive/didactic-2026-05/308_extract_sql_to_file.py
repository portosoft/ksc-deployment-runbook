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

# Let's search for keywords and extract contiguous printable blocks.
patterns = [
    rb'CREATE\s+TABLE\s+[a-zA-Z0-9_.]+',
    rb'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+[a-zA-Z0-9_.]+',
    rb'CREATE\s+SCHEMA',
    rb'ALTER\s+TABLE\s+[a-zA-Z0-9_.]+',
    rb'CREATE\s+UNIQUE\s+INDEX\s+[a-zA-Z0-9_.]+',
    rb'DROP\s+TABLE\s+[a-zA-Z0-9_.]+',
    rb'DROP\s+VIEW\s+[a-zA-Z0-9_.]+'
]

seen_offsets = set()

with open('/tmp/all_sql_blocks.txt', 'w', encoding='utf-8') as out_f:
    for pat in patterns:
        for match in re.finditer(pat, data, re.IGNORECASE):
            start = match.start()
            block_start = start
            while block_start > 0 and data[block_start] != 0 and (32 <= data[block_start] < 127 or data[block_start] in (10, 13)):
                block_start -= 1
            block_start += 1

            block_end = start
            while block_end < len(data) and data[block_end] != 0 and (32 <= data[block_end] < 127 or data[block_end] in (10, 13)):
                block_end += 1

            if block_start in seen_offsets:
                continue
            seen_offsets.add(block_start)

            chunk = data[block_start:block_end]
            if len(chunk) > 30:
                printable = chunk.decode('ascii', errors='ignore')
                out_f.write(f"=== Offset {block_start} ===\\n")
                out_f.write(printable)
                out_f.write("\\n" + "="*80 + "\\n")
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/extract_sql_to_file.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        # Run remote script
        stdin, stdout, stderr = client.exec_command("python3 /tmp/extract_sql_to_file.py")
        stdout.read() # Wait for it to finish

        # Download the result
        sftp = client.open_sftp()
        sftp.get("/tmp/all_sql_blocks.txt", "scratch/all_extracted_sql.txt")
        sftp.remove("/tmp/all_sql_blocks.txt")
        sftp.close()

        client.exec_command("rm -f /tmp/extract_sql_to_file.py")
        client.close()
        print("SQL blocks successfully extracted to scratch/all_extracted_sql.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
