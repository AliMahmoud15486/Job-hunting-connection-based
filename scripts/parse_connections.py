"""Turn a LinkedIn Connections.csv export into a list of companies with ranked contacts.

Usage: python3 -I scripts/parse_connections.py data/Connections.csv runs/<run>/network.json

Email addresses are dropped on purpose: they never leave this machine.
"""
import csv
import io
import json
import re
import sys

LEGAL_SUFFIXES = re.compile(
    r"[,.]?\s+(ltd|limited|gmbh|inc|llc|plc|ag|bv|sa|sas|srl|ab|oy|as|co|corp|corporation|company|group|studios?|games|dac|ug|ireland|europe|emea|international|technologies|technology|platforms|holdings)\.?$",
    re.IGNORECASE,
)

# Who to approach first: recruiting, then people who lead the hiring function, then everyone else.
RANK_RULES = [
    (1, re.compile(r"recruit|talent|hiring|people partner|\bhr\b|human resources|sourc", re.I)),
    (2, re.compile(r"(head|director|lead|manager|vp|chief|principal).*(art|design|creative|product|marketing|brand|ux|ui)"
                   r"|(art|design|creative|product|marketing|brand|ux|ui).*(head|director|lead|manager|vp)", re.I)),
    (3, re.compile(r"art|design|creative|product|marketing|ux|ui|motion|brand", re.I)),
]


# Not real employers: skip them so they never show up as "companies in the network".
PLACEHOLDER = re.compile(
    r"^(self[- ]?employed|freelance|freelancer|selbst(st|s)(ä|ae)ndig|independent|confidential.*|stealth.*|"
    r"open to work|looking for.*|unemployed|student|retired|n/?a|none|-+|\W*|upwork|fiverr|خاص|عمل خاص|عمل حر|صاحب عمل خاص/حر)$",
    re.IGNORECASE,
)


def company_key(name):
    key = name.strip().lower()
    previous = None
    while previous != key:
        previous = key
        key = LEGAL_SUFFIXES.sub("", key).strip()
    # \w is Unicode-aware, so Arabic, German etc. names keep their own keys.
    return re.sub(r"[\W_]+", " ", key).strip()


def contact_rank(position):
    for rank, pattern in RANK_RULES:
        if pattern.search(position or ""):
            return rank
    return 4


def read_rows(path):
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    # LinkedIn puts a few "Notes:" lines above the real header.
    start = next(i for i, line in enumerate(lines) if line.startswith("First Name"))
    return list(csv.DictReader(io.StringIO("\n".join(lines[start:]))))


def main(src, dest):
    companies, skipped = {}, 0
    for row in read_rows(src):
        company = (row.get("Company") or "").strip()
        if not company or PLACEHOLDER.match(re.sub(r"[\W_]+", " ", company).strip()):
            skipped += 1
            continue
        key = company_key(company)
        entry = companies.setdefault(key, {"key": key, "names": set(), "contacts": []})
        entry["names"].add(company)
        position = (row.get("Position") or "").strip()
        entry["contacts"].append({
            "name": f"{row.get('First Name', '').strip()} {row.get('Last Name', '').strip()}".strip(),
            "position": position,
            "url": (row.get("URL") or "").strip(),
            "connected_on": (row.get("Connected On") or "").strip(),
            "rank": contact_rank(position),
        })

    out = []
    for entry in companies.values():
        names = sorted(entry["names"], key=len)
        entry["contacts"].sort(key=lambda c: (c["rank"], c["name"]))
        out.append({
            "key": entry["key"],
            "company": names[0],
            "aliases": names[1:],
            "contacts": entry["contacts"],
        })
    out.sort(key=lambda c: (-len(c["contacts"]), c["company"].lower()))

    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"{sum(len(c['contacts']) for c in out)} contacts at {len(out)} companies -> {dest} "
          f"({skipped} rows skipped: no employer or a placeholder like Freelance/Confidential)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
