# Zork Clone — Build Blueprint

**Purpose:** Step-by-step build instructions for a fresh Claude session.
Read this file, then read `SPEC.md` for data models and content. Build in
the order listed. Do not skip steps.

---

## Pre-flight

1. Read `SPEC.md` end to end. It is the source of truth for all data models,
   content, behavior, and edge cases. This blueprint tells you *build order*;
   the spec tells you *what to build*.
2. Read `DESIGN.md` for high-level context (quick skim — the spec supersedes it).
3. You're in `/workspace/zork-clone`. Python 3 project. No virtualenv needed
   for the container, but create `pyproject.toml` for clean packaging.

---

## Phase 1: Scaffolding

**Goal:** Files exist, imports work, `python -m zork` prints "Hello" and exits.

### Step 1.1 — Create directory structure
```
zork/
├── __init__.py        # empty
├── __main__.py
├── parser.py
├── game.py
├── rooms.py
├── objects.py
└── errors.py
tests/
├── __init__.py        # empty (so pytest discovers tests)
├── test_parser.py
├── test_game.py
└── test_integration.py
```

### Step 1.2 — Create `pyproject.toml`
Minimal. Project name `zork-clone`, version `0.1.0`, requires-python `>=3.10`
(we use `X | Y` union types). One dev dependency: `pytest`.

### Step 1.3 — Stub `__main__.py`
```python
def main():
    print("You are standing in a dark place. This game doesn't exist yet.")

if __name__ == "__main__":
    main()
```

### Step 1.4 — Verify
Run `python -m zork` from the project root. Should print the stub message.

---

## Phase 2: Data Models

**Goal:** All dataclasses defined. Can instantiate rooms, objects, doors, effects.

### Step 2.1 — `game.py`: Define dataclasses
Implement all five dataclasses from the spec:
- `Room`
- `GameObject`
- `Door`
- `CrossRoomEffect`
- `GameState`

Use `from dataclasses import dataclass, field`. Use Python 3.10+ type hints
(`str | None`, not `Optional[str]`).

**Do NOT put game logic here yet.** Just the data structures.

### Step 2.2 — `rooms.py`: Define all 9 rooms
Hardcode the room data from the spec's Content Spec table. Each room is a
`Room(...)` instance. Export a function `build_rooms() -> dict[str, Room]`.

Key details:
- Hub exits: `{"north": "north", "south": "south", "east": "east", "west": "west", "up": "up", "down": "down"}`
- Bridge passages are just exits: east room gets `"down": "down"`, down room
  gets `"east": "east"` (in addition to their hub exits). Same for
  north↔west.
- Hidden rooms (`alcove`, `cell`) start with ONE exit back to their parent
  room. They do NOT appear in the parent room's exits until the door is opened.
- All rooms start with `visited=False`.
- Populate each room's `objects` list with the object IDs that start there
  (per content spec).

### Step 2.3 — `objects.py`: Define all 12 objects, 2 doors, 2 effects
Hardcode from the spec's Content Spec tables. Export three functions:
- `build_objects() -> dict[str, GameObject]`
- `build_doors() -> dict[str, Door]`
- `build_effects() -> list[CrossRoomEffect]`

Key details:
- `lever` and `bell_rope`: `use_response=None` (effects handle messaging).
- `iron_grate`: `player_operable=False`, `is_locked=True`, `is_open=False`.
  Direction `"south"`, target `"alcove"`. It lives in room `"down"`.
- `oak_door`: `player_operable=True`, `is_locked=True`, `is_open=False`.
  Direction `"west"`, target `"cell"`. It lives in room `"west"`.
- Lever effect: `toggle=True`, targets `iron_grate.is_open`.
- Bell rope effect: `toggle=False`, targets `oak_door.is_locked`.
  Set `target_value=False` (unlocking, not opening).
- Don't forget aliases: sword→["blade"], key→["skeletonkey"], journal→["diary"].
- Door aliases: give the grate `["bars"]` and the door `["oak"]` for usability.

### Step 2.4 — Wire up `GameState` construction
Add a `build_initial_state() -> GameState` function (put it in `game.py`).
It calls `build_rooms()`, `build_objects()`, `build_doors()`, `build_effects()`,
sets `current_room="hub"`, empty inventory.

### Step 2.5 — Verify
Write a quick throwaway test or just run in Python REPL:
```python
from zork.game import build_initial_state
state = build_initial_state()
assert len(state.rooms) == 9
assert len(state.objects) == 12
assert len(state.doors) == 2
assert len(state.effects) == 2
assert state.current_room == "hub"
```

---

## Phase 3: Parser

**Goal:** `parse("go north")` returns `ParseResult("go", "north")`. All
aliases and shortcuts work. Bad input returns `None`.

### Step 3.1 — `parser.py`: Implement `parse(raw: str) -> ParseResult | None`
Follow the spec's Input Processing section exactly:
1. Strip, lowercase.
2. Reject >256 chars.
3. Strip non-printable chars (< ASCII 32).
4. Empty → return None (caller prints snarky empty_input error).
5. Split on whitespace.
6. Apply aliases/shortcuts.
7. Match token pattern → return ParseResult or None.

**Important alias handling:**
- Single-token direction words (`n`,`s`,`e`,`w`,`u`,`d` AND `north`,`south`,
  etc.) → `ParseResult("go", full_direction)`
- Single-token `i` → `ParseResult("inventory", None)`
- Single-token `l` → `ParseResult("look", None)`
- Single-token `q` → `ParseResult("quit", None)`
- Two-token where verb is `get` → normalize to `take`
- Two-token where verb is `x` → normalize to `examine`
- Two-token where verb is `l` → normalize to `look`
- Unknown single token that's not a direction/shortcut → unknown verb error
- More than 2 tokens → too_many_words error

The parser does NOT print errors itself. It returns `None` and sets an error
type that the caller can use to pick from the error pool. Options:
- Return a tuple `(ParseResult | None, str | None)` where the string is the
  error category. OR
- Have parse() call an error printer directly (simpler).

Go with the simpler option: parse() prints the error and returns None. Import
the error function from errors.py.

### Step 3.2 — `test_parser.py`: Unit tests
Test every case from the spec's test list:
- `"go north"` → `ParseResult("go", "north")`
- `"north"` → `ParseResult("go", "north")`
- `"n"` → `ParseResult("go", "north")`
- `"look"` → `ParseResult("look", None)`
- `"l"` → `ParseResult("look", None)`
- `"inventory"` → `ParseResult("inventory", None)`
- `"i"` → `ParseResult("inventory", None)`
- `"quit"` → `ParseResult("quit", None)`
- `"q"` → `ParseResult("quit", None)`
- `"take sword"` → `ParseResult("take", "sword")`
- `"get sword"` → `ParseResult("take", "sword")`
- `"examine key"` → `ParseResult("examine", "key")`
- `"x key"` → `ParseResult("examine", "key")`
- `""` → `None`
- `"a b c"` → `None`
- `"x" * 300` → `None`
- `"flurble"` → `None`

### Step 3.3 — Run tests
`python -m pytest tests/test_parser.py -v`. All green before moving on.

---

## Phase 4: Error Messages

**Goal:** Every error category has a pool of 3+ snarky responses.

### Step 4.1 — `errors.py`: Implement error pools
A dict mapping category string to list of strings. A function
`get_error(category: str) -> str` that picks randomly.

14 categories from the spec:
- `unknown_verb`, `unknown_noun`, `cant_take`, `cant_drop`, `no_exit`,
  `already_open`, `already_closed`, `no_use`, `not_operable`, `door_locked`,
  `empty_input`, `too_many_words`, `too_long`, `examine_nothing`

Write 3 responses per category. Make them funny. Classic Zork energy. Examples:
- `unknown_verb`: "I don't know the word 'flurble'. I don't know a lot of
  words, but that one especially."
- `empty_input`: "I'm not a mind reader. Well, I am, and your mind is blank."

### Step 4.2 — Quick test
Just verify `get_error("unknown_verb")` returns a string. Don't test specific
text — the random pool makes that brittle.

---

## Phase 5: Command Dispatch

**Goal:** All verbs work. Game is playable but has no game loop yet (dispatch
is callable programmatically).

### Step 5.1 — `game.py`: Implement `dispatch(state: GameState, cmd: ParseResult) -> str`
Dispatch should return the output string (what gets printed). This makes it
testable — the caller (game loop) handles the printing.

Implement each verb handler per the spec's Command Dispatch section. Tackle
them in this order (simplest to hardest):

1. **`inventory`** — just list `state.inventory` display names. Easiest.
2. **`look`** (no noun) — call `describe_room(state)`. Returns room description.
3. **`quit`** — set `state.running = False` and return a farewell. (The
   confirmation prompt is handled in the game loop, not dispatch.)
4. **`go`** — check exit exists in current room, move player, call
   `describe_room` for new room.
5. **`examine`** — resolve noun, return object description. Also handle
   examining doors (show description_open or description_closed).
6. **`look` (with noun)** — delegate to examine.
7. **`take`** — resolve noun in room, check takeable, move to inventory.
8. **`drop`** — resolve noun in inventory, move to current room.
9. **`use`** — resolve noun, check effects list, apply or return use_response.
10. **`open`** — resolve noun to door, check player_operable/locked/already_open,
    add exits.
11. **`close`** — resolve noun to door, check player_operable/already_closed,
    remove exits.

### Step 5.2 — Implement helper: `resolve_noun(state, noun) -> GameObject | Door | None`
Follows the spec's Object Resolution order:
1. Room objects by noun/aliases
2. Inventory objects by noun/aliases
3. Doors in current room by noun/aliases
4. None

### Step 5.3 — Implement helper: `describe_room(state) -> str`
Follows the spec's Room Entry logic:
1. First visit → verbose description, mark visited
2. Revisit → short description
3. List objects in room (display_name)
4. List exits (direction names). Include doors that are currently open.
   For closed/visible doors, mention them in the description but don't list
   as an exit.

### Step 5.4 — Implement helper: `apply_effect(state, effect) -> str`
For the cross-room effect system:
1. Look up target (door or object) by target_id.
2. If `toggle=True` and already applied → reverse it.
3. Set the attribute to the value.
4. If target is a door and we changed `is_open`, update room exits accordingly.
5. Return the effect message.

Track "already applied" with a simple set on GameState — add an
`applied_effects: set[str]` field (set of effect trigger_object_ids, or just
use an index). Or just check the current value of the target attribute — if
it already equals `target_value`, it's been applied. For toggle, flip it.

### Step 5.5 — Handle `quit` confirmation
The `quit` flow is special: dispatch returns a "are you sure?" message, and
the game loop handles the y/n input. Add a `pending_quit: bool = False` field
to GameState. When `quit` is dispatched, set `pending_quit = True`. The game
loop checks this and reads another input for confirmation.

### Step 5.6 — `test_game.py`: Unit tests
Build a minimal GameState for each test (use `build_initial_state()` and
modify as needed).

Test cases per the spec:
- Move to valid exit → current_room changes
- Move to invalid exit → error, current_room unchanged
- Take a takeable object → removed from room, added to inventory
- Take a non-takeable object → error
- Take object not in room → error
- Drop object in inventory → removed from inventory, added to room
- Drop object not in inventory → error
- Examine object in room → returns description
- Examine object in inventory → returns description
- Examine nothing → error
- Open unlocked door → exit added
- Open locked door → locked error
- Open non-player-operable door → not operable error
- Open already-open door → already open error
- Close open door → exit removed
- Use lever → effect fires, grate opens
- Use lever again → effect toggles, grate closes
- Use rope → effect fires, door unlocks
- Use rope again → repeat message, no state change
- Use sword → snarky use_response
- Use something with no use_response → generic snark
- Resolve noun by primary noun → found
- Resolve noun by alias → found
- Resolve unknown noun → None

### Step 5.7 — Run tests
`python -m pytest tests/test_game.py -v`. All green.

---

## Phase 6: Game Loop

**Goal:** `python -m zork` starts the game. Playable end to end.

### Step 6.1 — `__main__.py`: Implement the real game loop
Per the spec's pseudocode:
1. Parse `--debug` flag, configure logging.
2. Build initial state.
3. Print welcome banner. Keep it short — game name, one-liner, "Type 'look'
   to look around."
4. Print starting room description.
5. Loop: input → parse → dispatch → print output.
6. Handle quit confirmation flow (check `pending_quit`).
7. Catch `KeyboardInterrupt`, `EOFError` → farewell, clean exit.
8. Catch `Exception` → log, friendly message, continue.

### Step 6.2 — Playtest manually
Run `python -m zork` and play through:
- Walk around all rooms
- Pick up and drop objects
- Try both cross-room effects (lever → grate, rope → door)
- Open the oak door after ringing the bell
- Walk into the hidden rooms
- Try bad input (empty, gibberish, too long)
- Ctrl+C to quit
- `quit` command

Fix anything broken.

---

## Phase 7: Integration Tests

**Goal:** Automated scripted playthroughs verify cross-room effects work.

### Step 7.1 — `test_integration.py`
Don't test via stdin/stdout capture (fragile). Instead, call `parse()` and
`dispatch()` programmatically against a real `GameState`:

**Test 1: Lever → Grate**
```
state = build_initial_state()
# go south
dispatch(state, parse("go south"))
assert state.current_room == "south"
# use lever
dispatch(state, parse("use lever"))
# go back to hub, then down
dispatch(state, parse("go north"))  # back to hub
dispatch(state, parse("go down"))
assert state.current_room == "down"
# verify grate is open and south exit exists
assert "south" in state.rooms["down"].exits
# walk into alcove
dispatch(state, parse("go south"))
assert state.current_room == "alcove"
```

**Test 2: Bell Rope → Oak Door**
```
state = build_initial_state()
# go up, use rope
dispatch(state, parse("go up"))
dispatch(state, parse("use rope"))
# go back to hub, then west
dispatch(state, parse("go down"))  # back to hub
dispatch(state, parse("go west"))
assert state.current_room == "west"
# open door (should be unlocked now)
dispatch(state, parse("open door"))
assert "west" in state.rooms["west"].exits  # exit to cell
# walk into cell
dispatch(state, parse("go west"))
assert state.current_room == "cell"
```

### Step 7.2 — Run all tests
`python -m pytest -v`. Everything green.

---

## Phase 8: Polish & Commit

### Step 8.1 — Room descriptions
Write the verbose and short descriptions for all 9 rooms. Keep them 2-3
sentences each. Atmospheric but not overwrought. The spec has flavor notes
per room — use those as the vibe.

### Step 8.2 — Object descriptions
Write the `examine` descriptions for all 12 objects. These can be 1-2
sentences. Flavor over function.

### Step 8.3 — Welcome banner
Something short. Classic text adventure energy:
```
ZORK CLONE
A cheap and dirty tribute to the classics.
Type 'help' to... just kidding. There is no help.
Type 'look' to look around.
```
(Note: there IS no help command. That's the joke.)

### Step 8.4 — Final playtest
Run through the whole game one more time. Check:
- [ ] All 9 rooms reachable
- [ ] All 12 objects examinable
- [ ] Lever toggles grate (open/close)
- [ ] Bell rope unlocks oak door (one-shot)
- [ ] Oak door opens/closes after unlock
- [ ] Bridge passages work (east↔down, north↔west)
- [ ] Inventory works (take/drop/list)
- [ ] Quit with confirmation works
- [ ] Ctrl+C exits cleanly
- [ ] Bad input gets snarky responses
- [ ] --debug flag shows logging

### Step 8.5 — Commit
Commit everything. Push to GitHub.

---

## Gotchas & Decisions Already Made

These are things that might trip you up. They're all resolved in the spec —
this is just a quick-reference:

1. **Nouns are single words.** The parser splits on whitespace and takes 2
   tokens max. Objects have a `noun` field ("sword") for parsing and a
   `display_name` field ("rusty sword") for display. Don't confuse them.

2. **`use` dispatch goes through CrossRoomEffect, not a callback.** Check the
   effects list for a match. No match → use_response or generic snark. There
   is no function pointer / callback key system.

3. **`iron_grate` is NOT player-operable.** `open grate` gives a snarky
   error. Only the lever controls it. The `oak_door` IS player-operable
   (once unlocked).

4. **Lever toggles. Bell rope doesn't.** Lever can open AND close the grate
   repeatedly. Bell rope unlocks the oak door once; using it again gives a
   "nothing happens" message.

5. **Doors are bidirectional.** When you open the oak door from the Cell Block
   side, the Abandoned Cell also gets an exit back. Don't forget the reverse
   exit.

6. **Hidden rooms don't show up in parent room exits until the door is open.**
   The Crypt doesn't list "south" as an exit until the grate is opened. The
   Cell Block doesn't list "west" until the oak door is opened.

7. **The `quit` command has a confirmation step.** It's not just
   `state.running = False`. The game asks "are you sure?" and waits for y/n.

8. **Object nouns and aliases are globally unique.** The resolve function
   doesn't need to handle ambiguity. If two objects shared a noun, that'd
   be a data bug.

9. **`describe_room` with `look` always shows the verbose description.**
   Only automatic room entry uses the first-visit/revisit logic. Explicit
   `look` (no noun) always shows verbose.

10. **Error messages are random per category.** Don't hardcode a single
    response. Use `random.choice()` from a pool. Tests should not assert
    specific error text.
