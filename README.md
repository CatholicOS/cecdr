# CECDR

The home of the **Common Ecclesiastical Circumscription Data Repository**, curated by the **Catholic Engineering Task Force** of the [Catholic Digital Commons Foundation](https://github.com/CatholicOS).

## What is CECDR?

The Common Ecclesiastical Circumscription Data Repository (CECDR) provides a canonicalized list of identifiers for the ecclesiastical circumscriptions of the Catholic Church — dioceses and archdioceses of the Latin Church, the eparchies, archeparchies and exarchates of the Eastern Catholic Churches, territorial prelatures and abbacies, apostolic vicariates, prefectures and administrations, military ordinariates, personal ordinariates, personal prelatures, and missions sui iuris.

"[Ecclesiastical circumscription](https://en.wikipedia.org/wiki/Ecclesiastical_circumscription)" (*circumscriptio ecclesiastica*) is the umbrella term the Holy See itself uses — in the Annuario Pontificio and in the daily Bollettino — for dioceses and every entity juridically comparable to them. It is deliberately broader than "particular Church" (can. 368), so that personal prelatures and other assimilated structures fall within scope, and it is rite-neutral, covering the Latin Church and the Eastern Catholic Churches alike.

## Why?

Canonical circumscription identifiers are needed wherever Catholic data references a diocese or diocese-like entity:

- **diocesan liturgical calendars**, as served by the [Liturgical Calendar API](https://github.com/Liturgical-Calendar/LiturgicalCalendarAPI);
- **diocesan proper eulogies** of the Roman Martyrology (*Proprium Martyrologii seu Appendix Martyrologii*, Praenotanda n. 38 as amended by the decree *Postquam Summus Pontifex*, 2021), which the [CRMEDR](https://github.com/CatholicOS/crmedr) plans to namespace by owner;
- parish directories, episcopal succession data, sacramental record systems, and any other application that must say *which* diocese it means.

## The identifier scheme (draft)

```
circ:<iso3166-1-alpha2>-<slug>
```

Examples: `circ:us-boston`, `circ:it-roma`, `circ:al-shkodre-pult`, `circ:us-portland-in-oregon` (homonymous sees are qualified by their civil region, matching official usage). The full proposal — including the treatment of Eastern circumscriptions, supranational structures, type-as-attribute, and identity across elevations, mergers and suppressions — is in [docs/schema-proposal.md](docs/schema-proposal.md). **All IDs are drafts pending committee review.**

## Repository contents

- [`data/circumscriptions.json`](data/circumscriptions.json) — the seed registry: 2,935 Latin-rite circumscriptions across 203 countries, generated from the Liturgical Calendar API's world dioceses index, each with its draft canonical ID, the API's `diocese_id` as a cross-reference key, name, nation, and (where available) civil province.
- [`data/circumscription_types.json`](data/circumscription_types.json) — the companion types registry: draft canonical IDs (`ctype:diocese`, `ctype:archeparchy`, `ctype:territorial-abbacy`, …) for the 16 canonical ranks and juridic forms a circumscription can hold, each with its Latin name, the church it belongs to, whether it is territorial, the title of the one who governs it, and the governing canon. Each circumscription's `type` field is a cross-reference into this file.
- [`docs/schema-proposal.md`](docs/schema-proposal.md) — the proposed schema and the open questions for the committee.
- [`scripts/generate_seed.py`](scripts/generate_seed.py) — regenerates the seed from the API's `world_dioceses.json`, validating every identifier and cross-reference before writing.
- [`scripts/test_generate_seed.py`](scripts/test_generate_seed.py) — unit tests: `python3 -m unittest discover -s scripts -v`.

## Companion registries

- [CESIDR](https://github.com/CatholicOS/cesidr) — the 24 Churches *sui iuris*. Each circumscription's `church_sui_iuris` field is an `esi:` cross-reference into it (`"church_sui_iuris": "esi:latin"`).
- [`data/circumscription_types.json`](data/circumscription_types.json) — canonical ranks, referenced by each circumscription's `type` field.

## Sources

The seed derives from the [Liturgical Calendar API](https://github.com/Liturgical-Calendar/LiturgicalCalendarAPI) (Apache-2.0). Enrichment sources under consideration: the Annuario Pontificio (the authoritative reference), and the public databases of [GCatholic](https://gcatholic.org/) and [Catholic-Hierarchy](https://www.catholic-hierarchy.org/) (as verification aids; their compiled data is not incorporated wholesale).
