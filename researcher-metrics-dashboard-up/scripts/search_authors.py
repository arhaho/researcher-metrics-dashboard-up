#!/usr/bin/env python3
import sys, requests, os

OPENALEX_MAILTO = os.getenv("OPENALEX_MAILTO", "arber.hoti@uni-pr.edu")

def search_authors(query: str, per_page=25):
    url = "https://api.openalex.org/authors"
    params = {"search": query, "per_page": per_page, "mailto": OPENALEX_MAILTO}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["results"]

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/search_authors.py \"First Last\"")
        sys.exit(1)
    query = sys.argv[1]
    results = search_authors(query)
    for a in results:
        key = a["id"].split("/")[-1]
        name = a.get("display_name")
        insts = [i.get("display_name") for i in (a.get("last_known_institutions") or [])]
        print(f"{key}\t{name}\t{', '.join(insts)}")

if __name__ == "__main__":
    main()
