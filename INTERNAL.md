# SPARC Project - Internal Notes

## Overview
Web application for managing SPARC (South Peninsula Area Republican Coalition) member data. Built with Flask + PostgreSQL, deployed on Railway.

## Architecture
- **Backend:** `app.py` — Flask app with REST API
- **Frontend:** `templates/index.html` — Single-page HTML with inline JS/CSS
- **Database:** PostgreSQL on Railway (project: `soothing-learning`)
- **Hosting:** Railway (service: `sparc-web`)

## Live URL
https://sparc-web-production.up.railway.app

## Database

### Connection
- **Railway:** Set via `DATABASE_URL` env var on the `sparc-web` service (references `${{Postgres.DATABASE_URL}}`)
- **Public proxy:** Available in Railway dashboard under Postgres service > Connect tab
- **Local:** `psql -d sparc`

### Tables

**member** (209 rows):
| Column | Type | Notes |
|---|---|---|
| id | SERIAL PRIMARY KEY | Auto-incrementing |
| firstname | TEXT | |
| lastname | TEXT | |
| phone | TEXT | |
| email | TEXT | |
| board_contact | TEXT | e.g. "Ellen", "Dee", "Board" |
| membership_level | TEXT | Bush, Eisenhower, Lincoln, Reagan, Roosevelt, family, individual, student |
| attendance_notes | TEXT | Parsed from spreadsheet attendance record |
| outreach_notes | TEXT | |
| tickets_feb_2026 | INTEGER | Feb 2026 event tickets |
| tickets_apr | INTEGER | April event tickets |
| active | BOOLEAN DEFAULT TRUE | FALSE for removed/moved/expired members |

**membership** (8 rows):
| id | level |
|---|---|
| 1-5 | Bush, Eisenhower, Lincoln, Reagan, Roosevelt |
| 6-8 | family, individual, student |

## API Endpoints
- `GET /` — Serve the HTML page
- `GET /api/members` — All members as JSON (supports `?search=` query param)
- `GET /api/members/<id>` — Single member as JSON
- `PUT /api/members/<id>` — Update member (JSON body with changed fields)
- `GET /api/membership_levels` — List of membership levels

## Data Import
- Source: `SPARC.xlsx` spreadsheet
- Import script: `import_sparc.py` (uses openpyxl + psycopg2)
- Parses attendance records to extract membership level and active status
- Column mapping: A=firstname, B=lastname, C=phone, D=board_contact, E=outreach_notes, F=attendance (parsed), G=email, H=tickets_feb, M=tickets_apr

## Files
| File | Purpose |
|---|---|
| `app.py` | Flask backend |
| `templates/index.html` | Frontend (inline JS/CSS) |
| `static/SPARC-logo.png` | Logo in header |
| `SPARC-logo.png` | Original logo file |
| `import_sparc.py` | Data import script |
| `SPARC.xlsx` | Source spreadsheet |
| `requirements.txt` | Python deps: flask, gunicorn, psycopg2-binary |
| `Procfile` | Railway/gunicorn config |

## Railway Setup
- **Project:** soothing-learning
- **Services:** Postgres, sparc-web
- **Env vars on sparc-web:** `DATABASE_URL=${{Postgres.DATABASE_URL}}`
- **Deploy:** `railway up` from project root (or push to linked GitHub repo)
- **CLI:** `brew install railway`, then `railway login`
- **Redeploy:** `railway service redeploy --service sparc-web --yes`

### Security Notes
- `DATABASE_URL` is required as an env var — never hardcode credentials in source
- On Railway, the sparc-web service references `${{Postgres.DATABASE_URL}}` so it auto-updates if Postgres vars change
- Credentials were rotated on 2026-02-10 after an accidental commit exposed the original password
- Used `git-filter-repo` to scrub the password from git history and force-pushed

## Local Development
```bash
# Run locally against local DB:
DATABASE_URL=postgresql:///sparc python3 app.py

# Run locally against Railway DB (get URL from Railway dashboard):
DATABASE_URL="postgresql://..." python3 app.py

# Open http://localhost:5001
```

## Known Issues
- Logo (`/static/SPARC-logo.png`) not displaying on Railway deployment — needs investigation
- Port 5000 is used by macOS AirPlay, so local dev uses port 5001
- GPG signing via Krypton may time out; use `--no-gpg-sign` if needed

## Session History
1. Imported SPARC.xlsx into local PostgreSQL using `import_sparc.py`
2. Created `member` and `membership` tables
3. Built Flask web app with inline-editing data table
4. Added SPARC logo to header
5. Installed Railway CLI, connected to existing project
6. Recreated member table on Railway with full schema (was outdated 4-column version)
7. Loaded all 209 members + 8 membership levels into Railway DB
8. Updated app.py to use Railway DATABASE_URL
9. Created Procfile + requirements.txt for deployment
10. Deployed to Railway via `railway up`
11. Generated public domain: https://sparc-web-production.up.railway.app
12. GitGuardian flagged exposed PostgreSQL URI in GitHub
13. Removed hardcoded credentials from app.py and INTERNAL.md; app now requires DATABASE_URL env var
14. Scrubbed password from git history with git-filter-repo, force-pushed cleaned history
15. Rotated database password on Railway (ALTER USER + updated all Postgres env vars)
16. Redeployed sparc-web, verified app works with new credentials
