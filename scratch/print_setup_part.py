def main():
    with open("scratch/setup.js", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Print a window around the configuration parsing
    start = 1139000
    end = 1141500
    print(content[start:end])

if __name__ == "__main__":
    main()
