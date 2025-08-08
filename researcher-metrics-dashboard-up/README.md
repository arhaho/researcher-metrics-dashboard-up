# Researcher Metrics Dashboard (OpenAlex, free)

A lightweight web app that **tracks authors you select** and **auto-refreshes every 24h** using the free [OpenAlex API].
No scraping. No paid keys. Deploy anywhere that serves static files (GitHub Pages, Netlify, Vercel).

**Key features**
- Total papers, total citations, h-index, i10-index per author
- Per-year papers and citations (last 10 years)
- Your tracked authors live in `scripts/authors.yml` (OpenAlex IDs **or** `name`+`institution`)
- A GitHub Action updates `frontend/data/snapshot.json` daily

> Why not Google Scholar? They do not provide a public API and scraping violates their Terms. OpenAlex is free, open, and stable.

## Quick Start

1) **Create a new GitHub repo** (private or public).  
2) **Download this ZIP**, extract, and push the contents to your repo.
3) Edit `scripts/authors.yml` to add or remove authors (use IDs **or** `name`+`institution`).  
   - Optional helpers: `scripts/search_authors.py` (find IDs by name) and `scripts/search_by_institution.py`.
4) In `scripts/refresh.py`, `OPENALEX_MAILTO` is set to your email for polite API usage.
5) Commit and push.  
6) **Enable GitHub Pages** or deploy `/frontend` to Netlify/Vercel (no build step).
7) The **daily refresh** GitHub Action runs at 03:00 UTC and updates `frontend/data/snapshot.json` automatically.

### Local preview
Open `frontend/index.html` in a browser, or run a simple server:
```bash
python3 -m http.server --directory frontend 8000
# open http://localhost:8000
```

### Files
- `scripts/authors.yml` — your static tracking list
- `scripts/refresh.py` — pulls from OpenAlex, writes `frontend/data/snapshot.json` (supports IDs or name+institution)
- `.github/workflows/refresh.yml` — schedules and commits daily refresh
- `frontend/` — static dashboard

### Data Source
- OpenAlex API. Docs: https://docs.openalex.org/

## License
MIT
