import paramiko
import os
import struct
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
import struct
import re
import os

with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

# Let's locate the strings first.
# Go compiler places all name strings in a big blob.
# Let's find all occurrences of 'migrations/postgres/'
name_prefix = b'migrations/postgres/'
name_matches = list(re.finditer(name_prefix, data))
print(f"Found {len(name_matches)} matches for {name_prefix}")

# Each file in embed.FS has:
# name_ptr (8 bytes)
# name_len (8 bytes)
# data_ptr (8 bytes)
# data_len (8 bytes)
# Total size of file struct = 32 bytes

# Let's find the ELF load base.
# For Go binaries, we can search for a name_ptr pointing to a known migration name offset.
# Let's try to find base address.
# A name pointer is: base_address + offset_in_file
# So name_ptr - offset_in_file = base_address.
# Let's look for a repeating base_address.

# We will scan the binary for 32-byte structures where:
# - name_len is between 30 and 120
# - name_ptr is in a reasonable range
# - data_len is between 5 and 500000
# - data_ptr is in a reasonable range

# Let's extract all candidate 32-byte structs.
candidates = []
for i in range(0, len(data) - 32, 8):
    name_ptr, name_len, data_ptr, data_len = struct.unpack('<QQQQ', data[i:i+32])
    # name_len should match migration path length
    if 35 <= name_len <= 150 and 5 <= data_len <= 500000:
        # Check if name_ptr is valid (in RAM range, e.g. base_address + offset)
        candidates.append((i, name_ptr, name_len, data_ptr, data_len))

print(f"Found {len(candidates)} candidate structs.")

# Let's find the base address by matching name_ptr to our name_matches offsets.
# If name_ptr - offset_in_file is constant, that's our base address!
base_address = None
base_votes = {}
for c_idx, name_ptr, name_len, data_ptr, data_len in candidates:
    # Try all filename offsets
    for m in name_matches:
        offset = m.start()
        # The filename string in memory starts at offset
        diff = name_ptr - offset
        if diff > 0 and (diff & 0xfff) == 0: # Usually page-aligned base address
            base_votes[diff] = base_votes.get(diff, 0) + 1

if base_votes:
    base_address = max(base_votes, key=base_votes.get)
    print(f"Detected Base Address: {hex(base_address)} (votes: {base_votes[base_address]})")
else:
    # Let's try non page-aligned just in case
    for c_idx, name_ptr, name_len, data_ptr, data_len in candidates:
        for m in name_matches:
            offset = m.start()
            diff = name_ptr - offset
            if diff > 0:
                base_votes[diff] = base_votes.get(diff, 0) + 1
    if base_votes:
        base_address = max(base_votes, key=base_votes.get)
        print(f"Detected Base Address (non-aligned): {hex(base_address)} (votes: {base_votes[base_address]})")

if not base_address:
    print("Could not detect base address.")
    exit(1)

# Now, resolve each candidate to its name and data
resolved_files = []
for c_idx, name_ptr, name_len, data_ptr, data_len in candidates:
    name_offset = name_ptr - base_address
    data_offset = data_ptr - base_address

    if 0 <= name_offset < len(data) and name_offset + name_len <= len(data):
        filename = data[name_offset:name_offset+name_len].decode('ascii', errors='ignore')
        if filename.startswith('migrations/postgres/'):
            if 0 <= data_offset < len(data) and data_offset + data_len <= len(data):
                file_content = data[data_offset:data_offset+data_len].decode('utf-8', errors='ignore')
                resolved_files.append((filename, file_content))

print(f"Resolved {len(resolved_files)} migration files.")

# Write them out to a folder
os.makedirs('/tmp/extracted_migrations', exist_ok=True)
for filename, content in resolved_files:
    # Clean up name to be safe
    safe_name = filename.replace('migrations/postgres/', '')
    # Sometimes it has garbage at the end
    safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '', safe_name)
    if safe_name.endswith('.sql'):
        with open(f'/tmp/extracted_migrations/{safe_name}', 'w', encoding='utf-8') as out_f:
            out_f.write(content)

print("Saved all migrations to /tmp/extracted_migrations/")
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/extract_embed.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/extract_embed.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/extract_embed.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
