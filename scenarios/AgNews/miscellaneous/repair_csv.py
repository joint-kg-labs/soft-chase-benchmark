import csv

INPUT_FILE = "../dataset/agnews500.csv"
OUTPUT_FILE = "../dataset/agnews_fixed_500.csv"
REPORT_FILE = "malformed_report.txt"

malformed_rows = []
clean_rows = []

def parse_id_int(raw: str, line_num: int) -> int:
    s = (raw or "").strip()
    try:
        return int(s)
    except ValueError:
        # Decide policy: fail fast (recommended so you don't silently corrupt ids)
        raise ValueError(f"Line {line_num}: id is not a valid integer: {raw!r}")

with open(INPUT_FILE, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

    # Read and preserve header
    header = next(reader, None)
    if header is None:
        raise RuntimeError("Empty CSV file.")
    # Expect header like: id,Title,Description (we preserve it exactly)
    clean_rows.append(header)

    for line_num, row in enumerate(reader, start=2):  # start=2 because header is line 1
        if len(row) != 3:
            malformed_rows.append((line_num, row))

            if len(row) >= 2:
                col1_raw = row[0]
                col2 = row[1]
                col3 = ",".join(row[2:])  # merge remainder into Description
            else:
                col1_raw = row[0] if row else ""
                col2 = ""
                col3 = ""

            col1 = parse_id_int(col1_raw, line_num)
            clean_rows.append([col1, col2, col3])
        else:
            col1 = parse_id_int(row[0], line_num)
            clean_rows.append([col1, row[1], row[2]])

# QUOTE_MINIMAL: will NOT quote integers, but will quote Title/Description if needed (commas/quotes/newlines)
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerows(clean_rows)

# Write report
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    if not malformed_rows:
        f.write("No malformed rows detected.\n")
    else:
        for line_num, row in malformed_rows:
            f.write(f"Line {line_num}: {row}\n")

print("✔ CSV repaired and saved as:", OUTPUT_FILE)
print("✔ Malformed rows report saved as:", REPORT_FILE)
