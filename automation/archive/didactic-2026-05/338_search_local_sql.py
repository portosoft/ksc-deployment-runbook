import re

def main():
    path = "scratch/all_extracted_sql.txt"
    if not os.path.exists(path):
        print(f"File {path} does not exist.")
        return

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Split by the separator "================================================================================"
    blocks = content.split("================================================================================")
    print(f"Total blocks in file: {len(blocks)}")

    keywords = ["view", "users", "challenges", "deleting_outbox", "workspace_id"]
    
    for kw in keywords:
        print(f"\n--- Search results for: {kw} ---")
        found = 0
        for i, block in enumerate(blocks):
            if kw.lower() in block.lower():
                found += 1
                # print first 500 chars of block
                header = block.split("\n")[0]
                body = "\n".join(block.split("\n")[1:25])
                print(f"Block {i} (Header: {header}):")
                print(body[:1500])
                print("-" * 40)
        print(f"Found {found} blocks containing '{kw}'.")

if __name__ == "__main__":
    import os
    main()
