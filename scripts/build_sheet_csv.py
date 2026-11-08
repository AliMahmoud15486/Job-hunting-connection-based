"""Build the Google Sheet CSV from scored jobs.

Usage: python3 -I scripts/build_sheet_csv.py runs/<run>
Reads scored.json, companies.json and (optionally) cv_links.json {job_id: url}; writes report.csv.
"""
import csv
import json
import os
import sys

COLUMNS = [
    "Company", "Role", "Position link", "Match score",
    "Contact name", "Contact title", "Contact LinkedIn URL",
    "Job poster", "Job poster LinkedIn URL", "Company match",
    "Industry", "Location / remote", "Posted", "Source",
    "Matched keywords", "Missing keywords", "Score reason",
    "Tailored CV link", "Other contacts at company",
]


def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(run_dir):
    scored = load(os.path.join(run_dir, "scored.json"), [])
    companies = {c["key"]: c for c in load(os.path.join(run_dir, "companies.json"), [])}
    cv_links = load(os.path.join(run_dir, "cv_links.json"), {})

    rows = []
    for job in sorted(scored, key=lambda j: -j.get("score", 0)):
        company = companies.get(job.get("company_key"), {})
        contacts = company.get("contacts", [])
        best, others = (contacts[0], contacts[1:]) if contacts else ({}, [])
        rows.append({
            "Company": job.get("company", ""),
            "Role": job.get("title", ""),
            "Position link": job.get("url", ""),
            "Match score": job.get("score", ""),
            "Contact name": best.get("name", ""),
            "Contact title": best.get("position", ""),
            "Contact LinkedIn URL": best.get("url", ""),
            "Job poster": " – ".join(x for x in [job.get("poster", {}).get("name", ""), job.get("poster", {}).get("title", "")] if x),
            "Job poster LinkedIn URL": job.get("poster", {}).get("url", ""),
            # "check": matched on a very short name only; confirm the contact works at the same company.
            "Company match": "check" if job.get("match_confidence") == "check" else "",
            "Industry": company.get("industry", ""),
            "Location / remote": job.get("location", ""),
            "Posted": job.get("posted", ""),
            "Source": ", ".join([job.get("source", "")] + job.get("also_seen_on", [])),
            "Matched keywords": ", ".join(job.get("matched_keywords", [])),
            "Missing keywords": ", ".join(job.get("missing_keywords", [])),
            "Score reason": job.get("reason", ""),
            "Tailored CV link": cv_links.get(job.get("id"), ""),
            "Other contacts at company": "; ".join(f"{c['name']} ({c['position']})" for c in others[:5]),
        })

    dest = os.path.join(run_dir, "report.csv")
    with open(dest, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} rows -> {dest}")


if __name__ == "__main__":
    main(sys.argv[1])
