"""
One-off migration script: pulls the /codes node from the existing Firebase
Realtime Database and writes it out as SQL INSERT statements matching
schema.sql, ready to paste into the Supabase SQL editor.

Usage:
    python migrate_from_firebase.py

Output:
    codes_import.sql   (in the same folder)
"""

import json
import requests

FIREBASE_DATABASE_URL = "https://mafia-certificate-default-rtdb.asia-southeast1.firebasedatabase.app"
OUTPUT_FILE = "codes_import.sql"


def fetch_codes():
    resp = requests.get(f"{FIREBASE_DATABASE_URL}/codes.json")
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise SystemExit("No data found at /codes.json")
    return data


def sql_literal(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def build_insert(code_key, entry):
    code = code_key
    type_ = entry.get("type")
    variable = entry.get("variable")
    screen = entry.get("screen")
    amount = entry.get("amount")
    active = entry.get("active", True)

    # Anything that isn't one of the known scalar fields goes into `value`
    # as jsonb, covering setdf/setbg-style entries.
    known_keys = {"type", "variable", "screen", "amount", "active"}
    extra = {k: v for k, v in entry.items() if k not in known_keys}
    value_json = json.dumps(extra) if extra else None

    columns = ["code", "type", "variable", "screen", "amount", "value", "active"]
    values = [
        sql_literal(code),
        sql_literal(type_),
        sql_literal(variable),
        sql_literal(screen),
        sql_literal(amount),
        f"{sql_literal(value_json)}::jsonb" if value_json else "NULL",
        sql_literal(active),
    ]
    return f"insert into codes ({', '.join(columns)}) values ({', '.join(values)}) on conflict (code) do nothing;"


def main():
    codes = fetch_codes()
    lines = [build_insert(key, entry) for key, entry in codes.items()]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(lines)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
