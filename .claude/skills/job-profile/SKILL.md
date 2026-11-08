---
name: job-profile
description: Build or refresh the candidate's master profile (data/profile.json) from their CV files and portfolio pages listed in config/settings.json. Step 1 of the job report. Use when the CV changed, when profile.json is missing, or when asked to "update the profile".
---

# job-profile — the single source of truth for every CV

Every later step (scoring, CV tailoring) may only use facts that are in `data/profile.json`. Nothing gets invented downstream, so this file must be complete and accurate.

## Inputs
- `config/settings.json`: `candidate_name`, `cv_files`, `portfolio_urls`, `home_location`, `work_rights`. If it's missing, tell the user to copy `config/settings.example.json` and fill it in, then stop.
- Each file in `cv_files` (PDF, .docx or text). A LinkedIn "Save to PDF" profile works well. Read them with the Read tool.
- Each URL in `portfolio_urls`: read with the built-in browser (`get_page_text`) and open the case-study or project pages they link to. Don't download files without asking.

## Output: `data/profile.json`
```json
{
  "name": "", "headline": "", "location": "", "work_rights": "", "open_to": "",
  "contact": {"email": "", "phone": "", "linkedin": "", "portfolio": [], "github": ""},
  "languages": [{"language": "", "level": ""}],
  "target_roles": [],
  "skills": {"<group>": []},
  "experience": [
    {"id": "exp-<company>", "company": "", "title": "", "start": "YYYY-MM", "end": "YYYY-MM|present",
     "location": "", "bullets": [{"id": "exp-<company>-1", "text": "", "keywords": [], "source": "cv|site"}]}
  ],
  "projects": [{"id": "proj-<name>", "name": "", "role": "", "context": "", "stack": [], "url": "", "bullets": []}],
  "research": [], "education": [], "certifications": [], "summary_facts": []
}
```
- Every bullet has a stable `id` and a `source`. `cv-tailor` cites these ids.
- `keywords` per bullet: the skills and tools that bullet actually shows evidence of (used for matching).
- `target_roles`: derived from the headline and any "open to" statement, plus close variants (e.g. Product Designer → UX Designer, UI Designer). Group skills however suits the person (e.g. art, product, engineering, tools, ai).

## Conflicts
Compare the sources. Write every disagreement (dates, company names, titles, levels) to `data/profile-conflicts.md` as a table: field · source A says · source B says · chosen.

If any "chosen" cell is empty, ask the user to settle it with AskUserQuestion and record the answers. Once resolved, later runs don't ask again. `cv-tailor` refuses to run while conflicts are open.

## Done when
`profile.json` lists every role in the CV, every project on the portfolio, and no unresolved conflicts remain.
