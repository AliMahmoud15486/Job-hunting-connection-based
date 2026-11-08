---
name: job-report
description: Run the whole connection-based job hunt — profile, job search, network match, scoring, tailored CVs — and export a Google Sheet of company, position link, match score and who to reach out to. Use for "/job-report", "find jobs in my network", "run the job report".
argument-hint: [industries] [country] [threshold]
---

# job-report — orchestrator

Each step is its own skill with its own files, so any step can be rerun alone. This skill asks the questions, runs the steps in order and exports.

## 0. Preflight
- `config/settings.json` exists (else: copy `config/settings.example.json`, fill it in, stop).
- The CV files and connections file it names exist.
- The Apify and Google Drive connectors are available in this session. If not, say which is missing.

## 1. Ask
With one AskUserQuestion call (prefilled from `settings.defaults`):
- Industries (multi-select).
- Country.
- Match threshold for tailored CVs (default from settings).
- Size: small test (~$0.25) or full (~$1.20).
Create `runs/<YYYY-MM-DD>-<country>-<industries-slug>/` and save the answers to `config.json` there.

## 2. Run the steps
1. `job-profile`: only if `data/profile.json` is missing, older than the CV files, or has unresolved conflicts.
2. `job-search` with the run dir, country and size (asks for cost approval).
3. `job-network` with the run dir and industries: parse, match jobs to the network, classify, filter → `jobs_to_score.json`.
4. `job-match` with the run dir.
5. `cv-tailor` with the run dir and threshold.
Stop and tell the user if a step produces nothing (no jobs, no network matches).

## 3. Export to Google Drive
1. Find or create the folder named in `google_drive_folder` (`search_files`, then `create_file` with `contentMimeType: application/vnd.google-apps.folder`), and inside it a folder named like the run.
2. For each tailored CV, upload its HTML copy with `create_file` (`textContent` = the HTML, `contentMimeType: text/html`, title `CV – <name> – <Company> – <Role>`). Drive turns it into a Google Doc. Don't upload .docx files as base64: copying a long encoded file through a tool call corrupts easily. The .docx files stay in `<run>/cvs/`. Save `{job_id: viewUrl}` to `<run>/cv_links.json`.
3. `python3 -I scripts/build_sheet_csv.py <run>` → `<run>/report.csv`.
4. Upload the CSV with `create_file`: `textContent` = the CSV, `contentMimeType: text/csv`, title `Job Report – <industries> – <country> – <date>`, parent = the run folder. Drive converts it to a Google Sheet. Each run makes a new sheet.

## 4. Report
Give the sheet link, the number of jobs found, matched and scored, how many reached the threshold, the top 5 (company, role, score, contact), and the Apify spend. Never contact anyone: the sheet only names who to approach.
