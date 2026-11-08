"""Map raw output of the Apify actor curious_coder/linkedin-jobs-scraper to the common job shape.

Usage: python3 -I scripts/map_linkedin.py runs/<run>/raw/linkedin-apify.json runs/<run>/raw/linkedin.json
"""
import json
import sys


def main(src, dest):
    with open(src, encoding="utf-8") as f:
        items = json.load(f)
    rows = []
    for item in items:
        if not item.get("title"):
            continue
        rows.append({
            "company": item.get("companyName", ""),
            "title": item["title"],
            "location": item.get("location", ""),
            "url": item.get("link") or item.get("applyUrl", ""),
            "apply_url": item.get("applyUrl", ""),
            "source": "LinkedIn",
            "posted": (item.get("postedAt") or "")[:10],
            "description": item.get("descriptionText", ""),
            "seniority": item.get("seniorityLevel", ""),
            "industries": item.get("industries", ""),
            "poster": {
                "name": item.get("jobPosterName", ""),
                "title": item.get("jobPosterTitle", ""),
                "url": item.get("jobPosterProfileUrl", ""),
            },
        })
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print(f"{len(rows)} jobs -> {dest}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
