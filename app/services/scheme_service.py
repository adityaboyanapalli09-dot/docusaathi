import json
from pathlib import Path


SCHEMES_FILE = Path(__file__).resolve().parent.parent / "scheme_data" / "schemas.json"


def load_schemes():
    with open(SCHEMES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_schemes():
    return load_schemes()


def get_categories():
    schemes = load_schemes()
    return sorted(set(scheme["category"] for scheme in schemes))


def get_schemes_by_category(category):
    schemes = load_schemes()

    return [
        scheme
        for scheme in schemes
        if scheme["category"].lower() == category.lower()
    ]


def search_schemes(query):
    schemes = load_schemes()
    query = query.lower().strip()

    if not query:
        return schemes

    results = []

    for scheme in schemes:
        searchable_text = " ".join([
            scheme.get("name", ""),
            scheme.get("category", ""),
            scheme.get("short_description", ""),
            scheme.get("who_is_it_for", ""),
            scheme.get("eligibility", ""),
            scheme.get("benefits", "")
        ]).lower()

        if query in searchable_text:
            results.append(scheme)

    return results