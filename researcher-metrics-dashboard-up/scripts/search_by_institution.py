#!/usr/bin/env python3
import sys, requests, os

OPENALEX_MAILTO = os.getenv("OPENALEX_MAILTO", "arber.hoti@uni-pr.edu")

def find_institution(name: str):
    url = "https://api.openalex.org/institutions"
    params = {"search": name, "per_page": 5, "mailto": OPENALEX_MAILTO}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    results = r.json()["results"]
    return results[0] if results else None

def authors_by_institution_id(inst_id: str, per_page=50, max_pages=4):
    url = "https://api.openalex.org/authors"
    page = 1
    while page <= max_pages:
        params = {
            "filter": f"affiliations.institution.id:{inst_id}",
            "per_page": per_page,
            "page": page,
            "mailto": OPENALEX_MAILTO,
        }
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        for a in data["results"]:
            key = a["id"].split("/")[-1]
            name = a.get("display_name")
            insts = [i.get("display_name") for i in (a.get("last_known_institutions") or [])]
            print(f"{key}\t{name}\t{', '.join(insts)}")
        if len(data["results"]) < per_page:
            break
        page += 1

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/search_by_institution.py \"University Name\"")
        sys.exit(1)
    inst_name = sys.argv[1]
    inst = find_institution(inst_name)
    if not inst:
        print("No matching institution found.")
        sys.exit(2)
    inst_id = inst["id"]  # e.g., https://openalex.org/I201448701
    display = inst["display_name"]
    print(f"# Found institution: {display} ({inst_id})")
    authors_by_institution_id(inst_id)

if __name__ == "__main__":
    main()
