def main():
    with open("scratch/setup.js", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Print a window around the configuration patch
    start = 1141300
    end = 1143000
    print(content[start:end])

if __name__ == "__main__":
    main()
