# CECDR schema proposal (draft for committee review)

## Identifier scheme

```
circ:<iso3166-1-alpha2>-<slug>
```

- **`circ:`** — namespace prefix (placeholder, like `mr:` in the CRMEDR, pending a
  committee decision on prefixes across the registries).
- **`<iso3166-1-alpha2>`** — lowercase ISO country code of the nation in which the
  circumscription's see is located. Supranational or extraterritorial structures use a
  reserved segment instead (see below).
- **`<slug>`** — the see name (not the full styled title), ASCII-folded, lowercase,
  hyphenated: `boston`, `roma`, `shkodre-pult`. Generic type words ("Diocese of",
  "Diocesi di") are stripped: the *type* is an attribute, not part of the identity.

### Rules

1. **Type is an attribute, not identity.** A diocese elevated to an archdiocese, or an
   apostolic prefecture raised to a vicariate and then to a diocese, keeps its ID — as
   in the CRMEDR, where a beatus's canonization changes status, not identity.
2. **Homonymous sees within a nation** are qualified by their civil region, following
   official usage where it exists: `circ:us-portland-in-oregon`,
   `circ:us-lafayette-in-indiana`.
3. **Renames and transfers of see** keep the ID (with the new name as an attribute and
   the old among historical names); **mergers** produce a new ID for the united
   circumscription, with the predecessors retained as suppressed entries pointing to
   the successor; **suppressed** circumscriptions keep their IDs and are flagged, never
   deleted — historical data must remain referenceable.
4. **Eastern circumscriptions** follow the same scheme; the church sui iuris is an
   attribute (`church_sui_iuris`: e.g. `latin`, `ukrainian`, `maronite`,
   `syro-malabar`), and where an eparchy shares a city with a Latin see the slug is
   qualified by the church: `circ:us-philadelphia` (Latin),
   `circ:us-philadelphia-ukrainian` (archeparchy).
5. **Supranational and extraterritorial structures** (e.g. personal prelatures,
   ordinariates for Eastern faithful covering several nations) use the reserved
   first segment `int` in place of a country code: `circ:int-opus-dei`. `int` is not
   an ISO 3166-1 alpha-2 code, so no collision is possible; `circ:va-<slug>` is *not*
   used for this (the Holy See is a real territory). The token choice remains open for
   committee confirmation. Military ordinariates are national by nature:
   `circ:it-ordinariato-militare`.

## Entry shape

```json
{
  "id": "circ:us-boston",
  "litcal_id": "boston_us",
  "name": "Archdiocese of Boston",
  "nation": "US",
  "province": "Massachusetts",
  "church_sui_iuris": "latin",
  "type": "ctype:archdiocese"
}
```

## Circumscription types

`type` is not a free string but a cross-reference into a companion registry,
`data/circumscription_types.json`, which mints a canonical ID for each canonical
rank or juridic form a circumscription can hold:

```
ctype:<slug>
```

`ctype:diocese`, `ctype:archeparchy`, `ctype:territorial-abbacy`,
`ctype:apostolic-vicariate`, `ctype:military-ordinariate`,
`ctype:personal-prelature`, and so on — 16 in all. Each entry carries the Latin
name (`name_la`, the Annuario's own nomenclature), the church to which the form
belongs (`latin`, `eastern`, `both`), whether it is territorial, the title of the
one who governs it, and the governing canon or document.

This follows the cross-registry convention already used in the family: COECDR
embeds CRPDR `rp:` IDs, CDOCTDR embeds CRMEDR `mr:` IDs. An entry therefore
reads `"type": "ctype:diocese"`, and `scripts/generate_seed.py` asserts that
every `type` resolves against the types registry.

The `ctype:` prefix is a placeholder on the same footing as `circ:`, pending the
namespace coordination in open question 1.

## Further attributes

Planned beyond the seed: `metropolitan` (the ID of the metropolitan see), `status`
(active | suppressed | merged_into:<id>), `historical_names`, `erected` (date of
erection), and external keys (`litcal_id` now; potentially GCatholic and
Catholic-Hierarchy keys as cross-references).

## Seed and its limits

The seed (`data/circumscriptions.json`) covers the 2,935 Latin-rite circumscriptions in
the Liturgical Calendar API's world index. Known gaps and flaws, in scope for
enrichment:

- **Eastern Catholic circumscriptions are absent** (the source index is Latin-rite).
- **`type` is null** throughout: the source names mix bare see names ("Lezhë") with
  styled ones ("Archdiocese of Boston"), so typing needs an authoritative pass
  (Annuario Pontificio).
- Two homonymous Chinese sees (`circ:cn-xinjiang-1/-2`) carry ordinal qualifiers
  pending proper disambiguation.
- The personal prelature of Opus Dei is supranational and therefore seeded as
  `circ:int-opus-dei` (rule 5) with no `nation`, even though the source index lists it
  under Italy; the source also mislabels the row "Diocesi di Lanusei" — a fix has been
  submitted upstream
  ([LiturgicalCalendarAPI PR #718](https://github.com/Liturgical-Calendar/LiturgicalCalendarAPI/pull/718)).

## Open questions for the committee

1. The namespace prefix (`circ:`) and its coordination with the other registries'
   prefixes.
2. The reserved segment for supranational structures (rule 5).
3. Whether to encode the church sui iuris in the slug only on collision (rule 4) or
   always for non-Latin circumscriptions.
4. The authority order for names: Annuario Pontificio Latin names vs. vernacular
   official names (the seed currently carries the API's names, which mix both).
5. Whether Ordinariates for Eastern-rite faithful without their own hierarchy, and
   pastoral structures like apostolic exarchates in the diaspora, need a dedicated
   type taxonomy beyond the Annuario's. Both are provisionally minted in
   `data/circumscription_types.json` (`ctype:ordinariate-for-eastern-faithful`,
   `ctype:apostolic-exarchate`) so the question can be decided against concrete
   entries rather than in the abstract.
6. Whether type IDs should be English (`ctype:territorial-abbacy`, as minted) or
   Latin (`ctype:abbatia-territorialis`), following CDOCTDR's use of the Latin
   lemma. The Latin name is carried as `name_la` either way, so this is a question
   about the identifier alone.
7. Whether patriarchal and major archiepiscopal sees warrant their own type IDs.
   They are presently archeparchies, with the dignity of the church *sui iuris*
   carried by `church_sui_iuris`; the Annuario lists them distinctly.
8. Verification of the `church` field in `data/circumscription_types.json`. It
   records which churches are known to use each form, but that is an empirical
   question answerable only by enumerating real circumscriptions — and the seed is
   still Latin-rite only. `ctype:territorial-abbacy` was initially classified
   `latin` and is in fact `both`: the Abbazia territoriale di Santa Maria di
   Grottaferrata is Byzantine, one of the three circumscriptions of the Chiesa
   bizantina cattolica in Italia. The forms still marked `latin` — territorial
   prelature, apostolic vicariate, apostolic prefecture, mission *sui iuris*,
   personal prelature — need the same check against the Annuario rather than
   against expectation.
