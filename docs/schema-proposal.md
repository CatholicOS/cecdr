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
- The personal prelature of Opus Dei is supranational and therefore seeded as
  `circ:int-opus-dei` (rule 5) with no `nation`, even though the source index lists it
  under Italy; the source also mislabels the row "Diocesi di Lanusei" — a fix has been
  submitted upstream
  ([LiturgicalCalendarAPI PR #718](https://github.com/Liturgical-Calendar/LiturgicalCalendarAPI/pull/718)).

## Identifier durability

Three cases are already on this repository's record. None is a mistake of execution; each
is what a name-derived identifier does when the name, the type, or the source index moves.

- **The strip rule is already broken at scale.** The scheme requires generic type words to
  be stripped, because "the *type* is an attribute, not part of the identity" — yet 58
  seeded IDs carry the Italian type word (`circ:it-arcidiocesi-di-acerenza`,
  `circ:it-arcidiocesi-di-agrigento`, `circ:it-arcidiocesi-di-amalfi-cava-de-tirreni`, and
  55 more), and 31 ordinariates carry theirs in ten languages:
  `circ:au-military-ordinariate-of-australia`, `circ:de-deutsches-militarordinariat`,
  `circ:it-ordinariato-militare-per-l-italia`, `circ:es-arzobispado-castrense-de-espana`,
  `circ:pl-ordynariat-polowy-wojska-polskiego`, `circ:sk-vojensky-ordinariat-slovenska`,
  `circ:hu-magyarorszagi-katonai-ordinariatus`, `circ:lt-lietuvos-kariuomenes-ordinariatas`,
  `circ:ba-vojni-ordinarijat-u-bosne-i-hercegovine`, `circ:br-ordinariado-militar-do-brasil`,
  and the rest. Those two cohorts are 89 of the seed's 2,935 entries (two further entries,
  `circ:fr-diocese-aux-armees-francaises` and `circ:us-archdiocese-for-the-military-services`,
  carry a type word outside them). Rule 1 holds that type is not identity; 89 identifiers
  record the opposite, and correcting them would rename 89 live IDs.
- **A live ID has already been renamed.** `circ:it-opus-dei` became `circ:int-opus-dei`
  (commit `5067fb8`) once the country segment proved wrong for a supranational personal
  prelature. The correction is right; what had to change to make it is the identifier that
  was supposed to be stable. "Seed and its limits" above records the same case.
- **Two sees are told apart by an ordinal.** `circ:cn-xinjiang-1` and `circ:cn-xinjiang-2`
  "carry ordinal qualifiers pending proper disambiguation" — an arbitrary fact about
  arrival order in the source index, not about either circumscription, and one that will be
  wrong for at least one of them the moment the disambiguation lands.

Each case dissolves when the canonical identifier is machine-readable and the
human-readable layer is guaranteed beside it — both, not one at the cost of the other:

```text
id:      R7kQp2mXf4LdTbz9Ns3Hc1        # canonical, machine-readable, minted once
                                       # (illustrative value: shape only, not a minted ID)
alias:   circ:it-arcidiocesi-di-acerenza   # permanent, resolvable, never reused
labels:  "Arcidiocesi di Acerenza"@it · "Archidioecesis Acheruntina"@la ·
         "Archdiocese of Acerenza"@en
type:    archdiocese                   # an attribute, exactly as rule 1 already asks
```

Under that shape the strip rule needs no enforcement, because no type word is load-bearing;
the Opus Dei correction changes `nation` and adds a label, leaving the alias
`circ:it-opus-dei` resolvable forever alongside `circ:int-opus-dei`; and the two Xinjiang
sees each hold a distinct canonical ID from the moment they are seeded, with the pending
disambiguation arriving as labels rather than as a renumbering.

The general argument — why canonical identifiers should be machine-readable, what that
costs, and how the human-readable layer is guaranteed rather than left optional — is set
out once in *Identifier Durability: Machine-Readable Canonical IRIs* (CDCF
`foundation-docs`, `research/identifier-durability-opaque-canonical-iris.md`) and is not
restated here.

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
6. Whether the canonical ID of a circumscription should be machine-readable and minted
   once, with every slug the scheme above produces (`circ:us-boston`,
   `circ:it-arcidiocesi-di-acerenza`, `circ:it-opus-dei`) kept as a permanent resolvable
   alias and every see name carried as a multilingual label — keeping this scheme intact
   as the human-readable layer rather than replacing it (see "Identifier durability").
