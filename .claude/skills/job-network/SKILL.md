---
name: job-network
description: Read the LinkedIn Connections.csv export, group connections by company, match them against found jobs, classify the matched companies' industries and keep the chosen ones. Step 2 of the job report. Use when asked which companies the network covers, or as part of /job-report.
argument-hint: <run-dir> <industries, comma separated>
---

# job-network — where can we get an introduction?

## Inputs
- The connections file named in `config/settings.json` (`connections_file`, default `data/Connections.csv`). To get it: LinkedIn → Settings → Data privacy → Download your data → "Download larger data archive" (Connections isn't in the small list) → unzip and copy only `Connections.csv`. If it's missing, say exactly that and stop.
- Run dir and chosen industries.

## 1. Parse
`python3 -I scripts/parse_connections.py <connections_file> <run>/network.json`
- Groups connections by normalised company name ("Acme Ltd", "Acme Inc." → one company; Unicode-aware, so non-Latin names stay distinct).
- Skips placeholder employers (Freelance, Self-employed, Confidential, Stealth, …). Add new ones to `PLACEHOLDER` in the script when you spot them.
- Ranks contacts: 1 recruiting/talent, 2 heads/leads of design, product, marketing or art, 3 people in those functions, 4 others.
- Drops email addresses. They never leave this machine.

## 2. Match jobs to the network (jobs-first, the default)
Real networks have thousands of companies, so don't classify them all. After `job-search` has written `<run>/jobs.json`:
`python3 -I scripts/match_jobs_to_network.py <run>`
writes `<run>/jobs_in_network.json` and `<run>/companies.json` (matched companies only). Matches on one-word names under 4 letters get `match_confidence: "check"`, shown in the sheet's "Company match" column. Confirm those by looking at the contact's title or profile URL.

For a small network (under ~500 companies) you may instead classify every company first and search per company. See "Company-first mode" below.

## 3. Classify the matched companies
Use `data/company-cache.json` first (keyed by company `key`). For the rest, classify from what you know: `{key, industry, sub_industry, confidence, checked: "YYYY-MM-DD"}`. For `low` confidence only, look the company up with Apify `apify--rag-web-browser` (tell the user how many lookups first). Save the results to the cache.

Industry labels: Gaming, Mobile Gaming, Ad Tech, Consumer & Big Tech, SaaS / B2B Software, Creative / Design Agency, Media & Entertainment, E-commerce / Retail, Fintech, Healthtech, Education, AR/VR, Consulting, Other.

## 4. Filter
Keep companies whose industry matches a chosen one (rewrite `companies.json` with only those, adding `industry` and `sub_industry`). Then write `<run>/jobs_to_score.json`: jobs at kept companies whose title matches the profile's `target_roles` family. Renumber `id` from J001.

## Company-first mode (small networks)
Classify every company in network.json, filter by industry, find each one's careers page, and let `job-search` query those boards directly.

## Report back
Connections, companies, rows skipped, jobs matched, companies kept per industry. Never print email addresses.
