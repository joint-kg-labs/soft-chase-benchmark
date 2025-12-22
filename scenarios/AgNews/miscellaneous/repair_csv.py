import csv
from pathlib import Path

INPUT_FILE = "../dataset/agnews.csv"
OUTPUT_FILE = "../dataset/agnews_fixed.csv"
REPORT_FILE = "malformed_report.txt"

malformed_rows = []

clean_rows = []

with open(INPUT_FILE, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

    for line_num, row in enumerate(reader, start=1):
        # Expected exactly 3 columns
        if len(row) != 3:
            malformed_rows.append((line_num, row))

            if len(row) >= 2:
                col1 = row[0]
                col2 = row[1]
                col3 = ",".join(row[2:])  # merge back together
            else:
                # Completely broken row
                col1 = row[0] if row else ""
                col2 = ""
                col3 = ""

            clean_rows.append([col1, col2, col3])

        else:
            clean_rows.append(row)

# Write repaired CSV with proper quoting
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
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
