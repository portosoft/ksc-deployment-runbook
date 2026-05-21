import os


def main():
    log_path = r"C:\Users\FábioMendes\.gemini\antigravity\brain\587fdae5-cebb-4fbc-817c-71812dc64c20\.system_generated\logs\overview.txt"
    if not os.path.exists(log_path):
        print(f"Log path does not exist: {log_path}")
        return

    print("Searching log file...")
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    matches = []
    for idx, line in enumerate(lines):
        if any(w in line.lower() for w in ["mfa", "totp", "login", "credential"]):
            matches.append((idx + 1, line.strip()))

    print(f"Found {len(matches)} matches.")
    # Show last 100 matches to see the recent context
    for idx, m in matches[-100:]:
        print(f"Line {idx}: {m[:120]}")


if __name__ == "__main__":
    main()
