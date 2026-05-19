import re


def main():
    with open("scratch/setup.js", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Let's search for keywords like eula, acceptEula, accept-eula, accept eula
    # inside setup.js and print their surroundings.
    patterns = [r"acceptEula", r"eula", r"accept", r"agree", r"privacy"]

    for pat_str in patterns:
        print(f"\n=== MATCHES FOR '{pat_str}' ===")
        # We can find matches and show a window of characters around them.
        for m in re.finditer(pat_str, content, re.IGNORECASE):
            start = max(0, m.start() - 150)
            end = min(len(content), m.end() + 150)
            snippet = content[start:end]
            # Replace whitespace to make it readable
            cleaned = " ".join(snippet.split())
            print(f"[{m.start()}]: ... {cleaned} ...")


if __name__ == "__main__":
    main()
