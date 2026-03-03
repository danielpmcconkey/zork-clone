# Zork Clone — Design Doc

## Status: Requirements locked, architecture TBD

## What We're Building
Python CLI text adventure. Cheap and dirty Zork clone focused on the engine
mechanics (parser, rooms, objects, interaction), not on story or polish.
Not a product — a demo.

## Decisions Made

### Parser
- Three input patterns:
  - **One-word:** `inventory`, `look`, `quit`, and bare directions (`north`,
    `south`, `east`, `west`, `up`, `down` as shortcuts for `go <direction>`)
  - **Two-word:** `verb noun` — the standard format
  - **No three-word commands.** No `use X on Y`, no `get X from Y`.
- Supported verbs: `go`, `get`/`take`, `drop`, `look`, `examine`, `open`,
  `close`, `use`, `inventory`, `quit`
- `look` with no noun = describe current room
- `look [noun]` and `examine [noun]` are synonyms — both inspect an object
- `examine` with no noun = error (snarky)
- `use` is one-arg, context-free: `use key` does the obvious thing based on
  the object's default action in the current context. No obvious action = snarky error.
- `quit` — one-word command, snarky confirmation prompt before exiting

### Rooms
- 9 total: hub (start) + 6 directional rooms + 2 hidden rooms behind doors
- All 6 directions off the hub: north, south, east, west, up, down
- 2 hidden dead-end rooms revealed by doors (reward for figuring out effects)
- 2 bridge passages that bypass the hub (BD picks which rooms they connect)
  - Bidirectional, always open (not gated behind interactions)
  - Player uses a direction to traverse them (room description tells you
    there's a passage in that direction)
- Verbose description on first visit, short description on revisit
- Theme: classic fantasy dungeon — underground, stone, torches

### Interaction
- 2 cross-room effects max. Boolean state only (on/off, open/closed).
  No chaining — A affects B, full stop. B does not cascade to C.
- Simple cause-and-effect is fine (lever opens grate, bell unlocks door).
  No multi-step puzzle chains. Bridges are always open.
- No combat
- No dark rooms / lighting mechanic
- No win/lose condition

### Objects
- 10-12 interactive objects across 9 rooms
- Mix of takeable items and stationary interactables
- Empty rooms are fine — not every room needs an object
- Minimum 0 objects per room, no enforced floor

### Inventory
- Yes, player has inventory
- No weight/capacity limits

### Open/Close
- Doors only. No containers.
- Opening a door reveals a passage (new exit becomes available)
- No inventory-inside-inventory, no `get X from Y`

### Parser Errors
- Snarky. Classic Zork energy. If it's not funny, we've failed.
- Implementation details (random pools vs fixed responses, context-awareness)
  are code decisions, not design decisions

### Other
- No save/load
- No combat (listed twice on purpose — scope creep prevention)

## Architecture
TBD — no code decisions made yet.
