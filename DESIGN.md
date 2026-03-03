# Zork Clone — Design Doc (WIP)

## Status: Design phase, not yet building

## What We're Building
Python CLI text adventure. Cheap and dirty Zork clone focused on the engine
mechanics (parser, rooms, objects, interaction), not on story or polish.
Not a product — a demo.

## Decisions Made

### Parser
- Strict 2-word `verb noun` format (like original Zork)
- Supported verbs: `go`, `get`/`take`, `drop`, `look`, `examine`, `open`, `close`, `use`, `inventory`

### Rooms
- 7 total: hub (start) + 6 directional rooms
- All 6 directions off the hub: north, south, east, west, up, down
- Some rooms cross-link to each other bypassing the hub (TBD which ones)
- Verbose description on first visit, short description on revisit

### Interaction
- Medium depth: objects you can pick up/examine, things that react (pull lever
  in one room affects another room), but NOT full puzzle dependency graphs
- No combat
- No dark rooms / lighting mechanic
- No win/lose condition

### Inventory
- Yes, player has inventory
- Second priority after core room/parser mechanics
- No weight/capacity limits planned

### Other
- No save/load
- No combat
- Story/theme: dealer's choice, steal from training data freely

## Open Questions (Dan hasn't answered yet)
1. **Cross-links between rooms** — Does Dan care which rooms connect to each
   other outside the hub, or is it dealer's choice?
2. **Object count** — Proposing 8-12 interactive objects across 7 rooms. Enough?
3. **Parser error personality** — Classic Zork had snarky error messages. Fun
   with it, or keep it dry?

## Architecture (not yet discussed)
TBD — no code decisions made yet. Will design after requirements are locked.
