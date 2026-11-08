"""Keep only jobs at companies where the network has contacts (jobs-first mode for big networks).

Usage: python3 -I scripts/match_jobs_to_network.py runs/<run>
Reads jobs.json and network.json; writes jobs_in_network.json and companies.json (matched companies only).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_connections import PLACEHOLDER, company_key  # noqa: E402
import re  # noqa: E402


def main(run_dir):
    with open(os.path.join(run_dir, "jobs.json"), encoding="utf-8") as f:
        jobs = json.load(f)
    with open(os.path.join(run_dir, "network.json"), encoding="utf-8") as f:
        network = json.load(f)

    by_key = {}
    for company in network:
        for name in [company["company"]] + company["aliases"]:
            by_key.setdefault(company_key(name), company)

    matched_jobs, matched = [], {}
    for job in jobs:
        name = job.get("company", "")
        if PLACEHOLDER.match(re.sub(r"[\W_]+", " ", name).strip()):
            continue  # "Confidential" employers can't be matched to anyone
        company = by_key.get(company_key(name))
        if company:
            job["company_key"] = company["key"]
            # One-word names under 4 letters (e.g. "Fin") often collide with unrelated companies.
            job["match_confidence"] = "check" if len(company["key"]) < 4 and " " not in company["key"] else "name"
            matched_jobs.append(job)
            matched[company["key"]] = company

    with open(os.path.join(run_dir, "jobs_in_network.json"), "w", encoding="utf-8") as f:
        json.dump(matched_jobs, f, ensure_ascii=False, indent=2)
    with open(os.path.join(run_dir, "companies.json"), "w", encoding="utf-8") as f:
        json.dump(list(matched.values()), f, ensure_ascii=False, indent=2)
    print(f"{len(matched_jobs)} of {len(jobs)} jobs are at {len(matched)} network companies")


if __name__ == "__main__":
    main(sys.argv[1])
