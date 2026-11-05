import sqlite3
import json
import sys

def inspect():
    conn = sqlite3.connect("honest_dev.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cursor.fetchall()]

    print("================================================================================")
    print("HONEST 4.0 - DATABASE TABLES OVERVIEW")
    print("================================================================================")

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        cols = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        row_count = cursor.fetchone()[0]

        print(f"\n[TABLE]: {table} ({row_count} rows)")
        print("-" * 70)
        col_summary = [f"{c['name']} ({c['type']})" for c in cols]
        print("Columns: " + ", ".join(col_summary))

        cursor.execute(f"SELECT * FROM {table};")
        rows = cursor.fetchall()
        for idx, row in enumerate(rows, 1):
            row_dict = dict(row)
            for k, v in row_dict.items():
                if isinstance(v, str) and len(v) > 75:
                    row_dict[k] = v[:72] + "..."
            print(f"  [{idx}]: {row_dict}")

    print("\n================================================================================")

if __name__ == "__main__":
    inspect()
