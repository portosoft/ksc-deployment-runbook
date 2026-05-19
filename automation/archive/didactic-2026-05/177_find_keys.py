import re


def main():
    with open("scratch/setup.js", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Search for occurrences of EULA, accept, json, args, argv, --
    # Let's search for matches of keywords
    keywords = [
        "acceptEula",
        "eula",
        "licen",
        "agree",
        "prompt",
        "config",
        "args",
        "argv",
        "setup-v3",
    ]

    print("--- Searching for keywords in setup.js ---")
    for kw in keywords:
        pattern = re.compile(r".{0,100}" + re.escape(kw) + r".{0,100}", re.IGNORECASE)
        matches = pattern.findall(content)
        print(f"Keyword '{kw}': {len(matches)} matches")
        # Print first 5 matches
        for m in matches[:5]:
            # clean up whitespace
            cleaned = " ".join(m.split())
            print(f"  Match: {cleaned}")


if __name__ == "__main__":
    main()
