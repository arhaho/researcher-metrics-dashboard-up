#!/usr/bin/env python3
import os, json, time, requests, yaml, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_OUT = ROOT / "frontend" / "data" / "snapshot.json"

# Set a contact email (recommended by OpenAlex)
OPENALEX_MAILTO = os.getenv("OPENALEX_MAILTO", "arber.hoti@uni-pr.edu")

def get_author(author_id: str):
    url = f"https://api.openalex.org/authors/{author_id}"
    params = {"mailto": OPENALEX_MAILTO}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def find_institution_id(inst_name: str):
    if not inst_name:
        return None
    url = "https://api.openalex.org/institutions"
    params = {"search": inst_name, "per_page": 1, "mailto": OPENALEX_MAILTO}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    results = r.json().get("results", [])
    return results[0]["id"] if results else None

def search_author_by_name(name: str, inst_id: str | None):
    url = "https://api.openalex.org/authors"
    params = {"search": name, "per_page": 25, "mailto": OPENALEX_MAILTO}
    if inst_id:
        params["filter"] = f"affiliations.institution.id:{inst_id}"
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    results = r.json().get("results", [])
    # Prefer exact (case-insensitive) match; else top result
    name_lc = (name or "").strip().lower()
    for a in results:
        if (a.get("display_name") or "").strip().lower() == name_lc:
            return a
    return results[0] if results else None

def slim_author(a: dict):
    display_name = a.get("display_name")
    openalex_id = a.get("id")
    ids = a.get("ids", {})
    works_count = a.get("works_count")
    cited_by_count = a.get("cited_by_count")
    counts_by_year = a.get("counts_by_year", []) or []
    summary_stats = a.get("summary_stats", {}) or {}
    last_known_institutions = a.get("last_known_institutions", []) or []
    updated_date = a.get("updated_date")
    inst_names = [i.get("display_name") for i in last_known_institutions if isinstance(i, dict)]

    return {
        "id": openalex_id,
        "openalex_key": openalex_id.split("/")[-1] if openalex_id else None,
        "display_name": display_name,
        "works_count": works_count,
        "cited_by_count": cited_by_count,
        "h_index": summary_stats.get("h_index"),
        "i10_index": summary_stats.get("i10_index"),
        "two_year_mean_citedness": summary_stats.get("2yr_mean_citedness"),
        "counts_by_year": counts_by_year,
        "institutions": inst_names,
        "updated_date": updated_date,
        "works_api_url": a.get("works_api_url"),
        "ids": ids,
    }

def main():
    cfg = yaml.safe_load(open(ROOT / "scripts" / "authors.yml", "r", encoding="utf-8"))
    author_specs = cfg.get("authors", [])

    out = {
        "generated_at_utc": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": "OpenAlex",
        "authors": [],
    }

    for spec in author_specs:
        try:
            if "id" in spec and spec["id"]:
                a = get_author(spec["id"])
            else:
                name = spec.get("name")
                inst_name = spec.get("institution")
                inst_id = find_institution_id(inst_name) if inst_name else None
                guess = search_author_by_name(name, inst_id)
                if not guess:
                    raise RuntimeError(f"No OpenAlex author found for {name} @ {inst_name}")
                # now fetch full author object by id to get latest stats
                full_id = guess["id"].split("/")[-1]
                a = get_author(full_id)
            out["authors"].append(slim_author(a))
            time.sleep(0.3)  # be gentle
        except Exception as e:
            out["authors"].append({
                "openalex_key": spec.get("id") or spec.get("name"),
                "error": str(e),
            })

    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"wrote {DATA_OUT}")

if __name__ == "__main__":
    main()
