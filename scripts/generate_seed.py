#!/usr/bin/env python3
"""Generate the CECDR seed registry from the Liturgical Calendar API's world
dioceses index (jsondata/world_dioceses.json, Apache-2.0).

The seed covers the Latin-rite circumscriptions known to the API; Eastern
eparchies and the other circumscription types are to be added from further
sources (see docs/schema-proposal.md).

Usage:
  python3 generate_seed.py /path/to/LiturgicalCalendarAPI/jsondata/world_dioceses.json [repo_root]
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

# Rows resolved manually, keyed by the API's diocese_id: homonymous sees the
# source index cannot disambiguate (no province field), and the personal
# prelature of Opus Dei, which is supranational (reserved segment `int`, no
# nation) and mislabeled in the source index (fix submitted upstream:
# Liturgical-Calendar/LiturgicalCalendarAPI#718).
MANUAL = {
    "xinjia_cn": {"slug": "xinjiang-1",
                  "note": "Two homonymous circumscriptions in the source "
                          "index; qualifier pending committee review."},
    "xinjin_cn": {"slug": "xinjiang-2",
                  "note": "Two homonymous circumscriptions in the source "
                          "index; qualifier pending committee review."},
    "opudei_it": {"slug": "opus-dei", "iso": "int", "nation": None,
                  "name": "Prelatura personale della Santa Croce e Opus Dei",
                  "type": "ctype:personal-prelature",
                  "note": "Supranational personal prelature: reserved segment "
                          "`int` instead of a country code (schema proposal, "
                          "rule 5). The source index lists it under Italy and "
                          "mislabels it 'Diocesi di Lanusei'; fix submitted "
                          "upstream (LiturgicalCalendarAPI PR #718)."},
}


def slugify(name):
    s = unicodedata.normalize("NFKD", name)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    # strip generic type prefixes so the slug is the see name. The source uses
    # four styled forms; Italian forms the archdiocese as "arcidiocesi", not
    # "archdiocesi", so it needs its own alternative rather than an `(arch)?`
    # prefix on the diocesan form.
    s = re.sub(r"^(arci)?diocesi di ", "", s)
    s = re.sub(r"^(arch)?diocese of ", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = json.load(open(sys.argv[1], encoding="utf-8"))
    repo_root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent
    entries = []
    for country in src["catholic_dioceses_latin_rite"]:
        iso = country["country_iso"].lower()
        rows = []
        for dio in country["dioceses"]:
            over = MANUAL.get(dio["diocese_id"], {})
            slug = over.get("slug") or slugify(dio["diocese_name"])
            rows.append((slug, over, dio))
        # Same-country homonyms: qualify with the province where the source
        # provides one (matching official usage, e.g. portland-in-oregon).
        counts = {}
        for slug, _, _ in rows:
            counts[slug] = counts.get(slug, 0) + 1
        for slug, over, dio in rows:
            if counts[slug] > 1 and dio.get("province"):
                slug = f"{slug}-in-{slugify(dio['province'])}"
            seg = over.get("iso", iso)
            entry = {
                "id": f"circ:{seg}-{slug}",
                "litcal_id": dio["diocese_id"],
                "name": over.get("name", dio["diocese_name"]),
                "nation": over["nation"] if "nation" in over else iso.upper(),
                "church_sui_iuris": "latin",
                "type": over.get("type"),
            }
            if dio.get("province"):
                entry["province"] = dio["province"]
            if over.get("note"):
                entry["note"] = over["note"]
            entries.append(entry)
    ids = [e["id"] for e in entries]
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"duplicate ids: {sorted(dupes)[:10]}"
    # Every `type` is a cross-reference into data/circumscription_types.json;
    # a typo there would silently produce an unresolvable reference.
    types_path = repo_root / "data" / "circumscription_types.json"
    known = {t["id"] for t in json.load(open(types_path, encoding="utf-8"))["entries"]}
    unknown = {e["type"] for e in entries if e["type"] and e["type"] not in known}
    assert not unknown, f"unknown circumscription types: {sorted(unknown)}"
    out = {
        "$comment": "CECDR seed registry: draft canonical IDs for Catholic "
                    "ecclesiastical circumscriptions, generated from the "
                    "Liturgical Calendar API's Latin-rite world dioceses index. "
                    "All IDs are drafts pending committee review; `type` is "
                    "null pending enrichment (see docs/schema-proposal.md).",
        "id_scheme": "circ:<iso3166-1-alpha2>-<slug>",
        "entry_count": len(entries),
        "entries": entries,
    }
    path = repo_root / "data" / "circumscriptions.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {len(entries)} circumscriptions to {path}")


if __name__ == "__main__":
    main()
