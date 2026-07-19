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
   ordinariates for Eastern faithful covering several nations) use a reserved first
   segment in place of the country code — proposal: `circ:va-<slug>` is *not* used for
   this (the Holy See is a real territory); instead a non-ISO reserved token `xx` or
   `int` is proposed, e.g. `circ:int-opus-dei`. **Open question** for the committee.
   Military ordinariates are national by nature: `circ:it-ordinariato-militare`.

## Entry shape

```json
{
  "id": "circ:us-boston",
  "litcal_id": "boston_us",
  "name": "Archdiocese of Boston",
  "nation": "US",
  "province": "Massachusetts",
  "church_sui_iuris": "latin",
  "type": "archdiocese"
}
```

Planned attributes beyond the seed: `type` (diocese, archdiocese, eparchy,
archeparchy, exarchate, territorial_prelature, territorial_abbacy,
apostolic_vicariate, apostolic_prefecture, apostolic_administration,
military_ordinariate, personal_ordinariate, personal_prelature, mission_sui_iuris),
`metropolitan` (the ID of the metropolitan see), `status`
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
- One source row is mislabeled (`opudei_it` as "Diocesi di Lanusei"); recorded as
  `circ:it-opus-dei` with a note, pending correction upstream in the Liturgical
  Calendar API.

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
   type taxonomy beyond the Annuario's.
