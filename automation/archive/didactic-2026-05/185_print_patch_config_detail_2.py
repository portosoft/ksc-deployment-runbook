def main():
    with open("scratch/setup.js", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Print a window around index 1131000 to 1134000
    start = 1131000
    end = 1134000
    print(content[start:end])


if __name__ == "__main__":
    main()
