"""Merge job posts from several sources, drop duplicates and stale posts.

Usage: python3 -I scripts/dedupe_jobs.py runs/<run>/jobs.json runs/<run>/raw/*.json [--max-age-days 30]

Each input file is a JSON list already mapped to the common shape:
  {company, company_key (optional; computed from company), title, location, url, source, posted (YYYY-MM-DD or ""), description}
"""
import json
import os
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_connections import company_key  # noqa: E402

AGGREGATORS = re.compile(r"linkedin\.com|indeed\.|glassdoor\.|google\.com|ziprecruiter|jooble|talent\.com|simplyhired", re.I)
SENIORITY_NOISE = re.compile(r"\b(m/w/d|f/m/d|m/f/d|w/m/d|h/f|remote|hybrid|full[- ]time|part[- ]time)\b|\(.*?\)|\s[-–|]\s.*$", re.I)


def norm(text):
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def job_key(job):
    title = norm(SENIORITY_NOISE.sub("", job.get("title", "")))
    city = norm((job.get("location") or "").split(",")[0])
    return (job["company_key"], title, city)


def better(a, b):
    """Prefer the company's own link, then the longer description."""
    a_direct = not AGGREGATORS.search(a.get("url") or "")
    b_direct = not AGGREGATORS.search(b.get("url") or "")
    if a_direct != b_direct:
        return a if a_direct else b
    return a if len(a.get("description") or "") >= len(b.get("description") or "") else b


def main(args):
    max_age = 30
    if "--max-age-days" in args:
        i = args.index("--max-age-days")
        max_age = int(args[i + 1])
        del args[i:i + 2]
    dest, sources = args[0], args[1:]
    cutoff = (date.today() - timedelta(days=max_age)).isoformat()

    merged, total, stale = {}, 0, 0
    for path in sources:
        with open(path, encoding="utf-8") as f:
            jobs = json.load(f)
        for job in jobs:
            total += 1
            job.setdefault("company_key", company_key(job.get("company", "")))
            if job.get("posted") and job["posted"] < cutoff:
                stale += 1
                continue
            key = job_key(job)
            if key in merged:
                kept = better(merged[key], job)
                kept.setdefault("also_seen_on", [])
                other = job if kept is merged[key] else merged[key]
                kept["also_seen_on"] = sorted(set(kept["also_seen_on"] + [other.get("source", "")] + other.get("also_seen_on", [])))
                merged[key] = kept
            else:
                merged[key] = job

    out = sorted(merged.values(), key=lambda j: (j.get("company", "").lower(), j.get("title", "").lower()))
    for i, job in enumerate(out, 1):
        job["id"] = f"J{i:03d}"
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"{total} posts in, {stale} older than {max_age} days, {len(out)} unique -> {dest}")


if __name__ == "__main__":
    main(sys.argv[1:])
