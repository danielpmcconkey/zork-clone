# Zork Clone — Functional Spec

## Overview
Python 3 CLI text adventure. Single-file entry point, modular internals.
No external dependencies — stdlib only (pytest for tests).

---

## Module Structure

```
zork-clone/
├── pyproject.toml         # minimal packaging metadata
├── zork/
│   ├── __init__.py        # empty
│   ├── __main__.py        # entry point, game loop
│   ├── parser.py          # input parsing
│   ├── game.py            # game state, command dispatch
│   ├── rooms.py           # room definitions and map
│   ├── objects.py         # object definitions and behaviors
│   └── errors.py          # snarky error messages
└── tests/
    ├── test_parser.py
    ├── test_game.py
    └── test_integration.py
```

Run with: `python -m zork`
Dev install: `pip install -e .`

Content (rooms, objects, doors, effects) is hardcoded as Python data
structures in `rooms.py` and `objects.py`. No external data files, no
JSON/YAML loading.

---

## Data Model

### Room
```python
@dataclass
class Room:
    id: str                          # e.g. "hub", "north_room"
    name: str                        # e.g. "The Great Hall"
    description: str                 # verbose, shown on first visit
    short_description: str           # shown on revisit
    exits: dict[str, str]            # direction -> room_id
    objects: list[str]               # object_ids currently in this room
    visited: bool = False            # tracks first visit
```

Exits are directional strings: `"north"`, `"south"`, `"east"`, `"west"`,
`"up"`, `"down"`. Bridge passages use these same directions — they're just
exits that skip the hub.

### GameObject
```python
@dataclass
class GameObject:
    id: str                          # e.g. "rusty_key"
    noun: str                        # parser-facing single word: "key"
    display_name: str                # pretty-print: "skeleton key"
    description: str                 # shown on examine/look
    takeable: bool                   # can the player pick this up?
    use_response: str | None         # object-specific snarky use text, or None for generic
    aliases: list[str]               # alternative single-word nouns the parser accepts
```

**Naming convention:** `noun` is the single word the player types. `display_name`
is what appears in room descriptions and inventory listings. `aliases` are
additional single words that resolve to this object (e.g. `["blade"]` for the
sword). Object nouns and aliases must be globally unique — no two objects may
share a noun or alias.

### Door
```python
@dataclass
class Door:
    id: str
    noun: str                        # parser-facing: "door", "grate"
    display_name: str                # pretty-print: "oak door", "iron grate"
    description_open: str
    description_closed: str
    description_locked: str          # shown when player tries to open a locked door
    room_id: str                     # room the door is in
    direction: str                   # direction it opens to
    target_room_id: str              # where it leads
    is_open: bool = False
    is_locked: bool = False          # locked doors must be unlocked before opening
    player_operable: bool = True     # can the player open/close this directly?
    aliases: list[str] = field(default_factory=list)
```

**Door states:**
- `is_locked=True, is_open=False` — locked and closed. `open` → snarky error
  about it being locked. Cross-room effect can set `is_locked=False`.
- `is_locked=False, is_open=False` — unlocked but closed. `open` → opens it,
  adds exit.
- `is_locked=False, is_open=True` — open. `close` → closes it, removes exit.
- `player_operable=False` — `open`/`close` commands give a snarky error
  ("It won't budge by hand."). Only cross-room effects can change state.

When opened: `room.exits[direction] = target_room_id`
When closed: `del room.exits[direction]`

Doors are bidirectional — the corresponding exit in the target room is also
added/removed.

### CrossRoomEffect
```python
@dataclass
class CrossRoomEffect:
    trigger_object_id: str           # object that causes the effect
    trigger_action: str              # "use" (always "use" for now)
    target_type: str                 # "door" or "object"
    target_id: str                   # door or object id being affected
    target_attribute: str            # what changes (e.g. "is_open", "is_locked")
    target_value: bool               # what it changes to
    message: str                     # shown to player when triggered
    toggle: bool = False             # if True, re-triggering reverses the effect
```

Max 2 of these in the entire game. Boolean state only. No chaining.

### GameState
```python
@dataclass
class GameState:
    rooms: dict[str, Room]
    objects: dict[str, GameObject]
    doors: dict[str, Door]
    effects: list[CrossRoomEffect]
    inventory: list[str]             # object_ids player is carrying
    current_room: str                # room_id
    running: bool = True             # False after quit confirmed
```

---

## Parser

### Input Processing
1. Read line from stdin, strip whitespace, lowercase
2. Reject input longer than 256 characters — snarky error about verbosity
3. Strip non-printable characters (anything below ASCII 32 except newline)
4. Empty input → snarky nudge, re-prompt
5. Split on whitespace into tokens

### Token Patterns

| Tokens | Interpretation |
|--------|---------------|
| `["north"]` (or any direction) | `("go", "north")` |
| `["inventory"]` | `("inventory", None)` |
| `["look"]` | `("look", None)` |
| `["quit"]` | `("quit", None)` |
| `[verb, noun]` | `(verb, noun)` |
| Anything else | Error — too many words or unrecognized |

### Direction Shortcuts
Bare directions (`north`, `south`, `east`, `west`, `up`, `down`, `n`, `s`,
`e`, `w`, `u`, `d`) are rewritten to `("go", direction)` before dispatch.

### Verb Aliases
- `get` → `take` (internally normalized to `take`)
- `n`/`s`/`e`/`w`/`u`/`d` → full direction name
- `i` → `inventory`
- `l` → `look`
- `q` → `quit`
- `x` → `examine`

### Parse Result
```python
@dataclass
class ParseResult:
    verb: str
    noun: str | None
```

On parse failure, return `None` and print a snarky error.

---

## Command Dispatch

`game.py` receives a `ParseResult` and dispatches:

| Verb | Noun | Behavior |
|------|------|----------|
| `go` | direction | Move to room via that exit. Error if no exit. |
| `look` | `None` | Print current room description (always verbose). |
| `look` | noun | Same as `examine`. |
| `examine` | noun | Print object description. Object must be in room or inventory. |
| `examine` | `None` | Snarky error. |
| `take` | noun | Move object from room to inventory. Must be `takeable`. |
| `drop` | noun | Move object from inventory to room. |
| `open` | noun | Open a door. Must be unlocked, closed, and `player_operable`. |
| `close` | noun | Close a door. Must be open and `player_operable`. |
| `use` | noun | Trigger cross-room effect if one matches. Otherwise, print `use_response` (object-specific snark) or generic snark if `None`. |
| `inventory` | — | List inventory contents, or "You're carrying nothing." |
| `quit` | — | Snarky confirmation prompt. `y` → exit. Anything else → continue. |

### `use` Dispatch (MJ-5 resolution)
The `use` command does NOT use a callback mechanism. Dispatch logic:
1. Resolve the noun to an object (room, inventory, or door).
2. Check the `effects` list for any `CrossRoomEffect` where
   `trigger_object_id == object.id` and `trigger_action == "use"`.
3. If match found → apply effect (set target attribute, print message). If
   `toggle=True` and effect was already applied, reverse it.
4. If no match → print `object.use_response` if set, otherwise generic
   snarky "no use" error.

### `open` Dispatch
1. Resolve noun to a door.
2. If `player_operable=False` → snarky error ("It won't budge by hand.")
3. If `is_locked=True` → print `description_locked`
4. If `is_open=True` → snarky "already open" error
5. Set `is_open=True`, add exit to room and target room.

### `close` Dispatch
1. Resolve noun to a door.
2. If `player_operable=False` → snarky error
3. If `is_open=False` → snarky "already closed" error
4. Set `is_open=False`, remove exit from room and target room.

### Object Resolution
When a command references a noun:
1. Check objects in current room by `noun` or `aliases`
2. Check objects in inventory by `noun` or `aliases`
3. Check doors in current room by `noun` or `aliases`
4. No match → snarky error ("You don't see that here.")

Object nouns and aliases are globally unique. No ambiguity possible.

### Cross-Room Effect Resolution
After any successful `use` action, check `effects` list. If the action
matches a trigger, apply the effect and print the message. The player sees
something like: *"You hear a grinding sound from somewhere below..."*

If `toggle=True`: track whether the effect has been applied. Re-triggering
reverses the target attribute to `not target_value` and prints a different
message (or the same message, implementation's call).

### Room Entry
When player enters a room:
1. If `visited` is `False`: print `name` + `description`, set `visited = True`
2. If `visited` is `True`: print `name` + `short_description`
3. List visible objects in the room (using `display_name`)
4. List visible exits (including any door-gated exits that are currently open)

---

## Game Loop (`__main__.py`)

```python
import logging

def main():
    if "--debug" in sys.argv:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stderr,
                            format="[DEBUG] %(message)s")

    game_state = build_initial_state()
    print(WELCOME_BANNER)
    describe_room(game_state)

    while game_state.running:
        try:
            raw = input("> ")
            result = parse(raw)
            if result is None:
                continue
            dispatch(game_state, result)
        except (KeyboardInterrupt, EOFError):
            print("\nFleeing so soon? Until next time...")
            break
        except Exception:
            logging.exception("Unexpected error during dispatch")
            print("Something went wrong. The dungeon shudders, then stabilizes.")
            continue
```

- `KeyboardInterrupt` and `EOFError` → farewell message, clean exit (exit 0)
- Unhandled exceptions → log to debug, print friendly in-game message, continue
- Piped input (`echo "look" | python -m zork`) hits `EOFError` after last
  line and exits cleanly
- `--debug` flag enables verbose logging to stderr (room transitions, object
  resolution, effect triggers)

---

## Error Messages (`errors.py`)

Pool of snarky responses per error category. Pick randomly from the pool
each time.

Categories:
- `unknown_verb` — verb not recognized
- `unknown_noun` — noun not found in room or inventory
- `cant_take` — object exists but isn't takeable
- `cant_drop` — object not in inventory
- `no_exit` — tried to go a direction with no exit
- `already_open` — door already open
- `already_closed` — door already closed
- `no_use` — generic: object has no use action and no use_response
- `not_operable` — tried to open/close something that only responds to effects
- `door_locked` — tried to open a locked door (may use door's description_locked instead)
- `empty_input` — player hit enter with nothing
- `too_many_words` — more than 2 tokens
- `too_long` — input exceeds 256 characters
- `examine_nothing` — `examine` with no noun

Minimum 3 responses per category.

---

## Room Map

```
                     [North Room]
                          |
             [West Room]--[HUB]--[East Room]
                 |                    |
          [Abandoned Cell]       [South Room]
          (behind oak door)
                             [Up Room] (above hub)
                             [Down Room] (below hub)
                                  |
                            [Hidden Alcove]
                            (behind iron grate)
```

Bridge passages (always-open, bidirectional):
- **East Room ↔ Down Room** — a crumbling spiral staircase
- **North Room ↔ West Room** — a narrow crawlspace

Hidden rooms (behind doors, dead-ends):
- **Hidden Alcove** — behind iron grate in the Crypt (one exit back north)
- **Abandoned Cell** — behind oak door in the Cell Block (one exit back east)

---

## Content Spec

### Theme
Classic fantasy dungeon. Underground stone corridors, torchlight, dust,
cobwebs. Not trying to be original.

### Rooms (9)

| ID | Name | Flavor |
|----|------|--------|
| `hub` | The Crossroads | Central chamber, passages in all directions |
| `north` | The Armory | Weapon racks, mostly empty |
| `south` | The Cistern | Underground pool, dripping water |
| `east` | The Library | Collapsed shelves, scattered books |
| `west` | The Cell Block | Rusted iron bars, old bones |
| `up` | The Bell Tower | Rickety stairs, cracked bell |
| `down` | The Crypt | Stone sarcophagi, cold air |
| `alcove` | The Hidden Alcove | Tiny chamber, something glints in the dust |
| `cell` | The Abandoned Cell | Scratched walls, a pile of rags in the corner |

### Objects (12)

| ID | Room | Noun | Display Name | Takeable | Use Response |
|----|------|------|-------------|----------|-------------|
| `torch` | hub | `torch` | brass torch | yes | "You wave the torch around. Nothing happens, because this isn't that kind of game." |
| `sword` | north | `sword` | rusty sword | yes | "You swing at the darkness. The darkness is unimpressed." |
| `shield` | north | `shield` | dented shield | yes | "You raise the shield heroically. No one is watching." |
| `lever` | south | `lever` | iron lever | no | `None` — triggers cross-room effect; `use_response` is never reached |
| `coin` | south | `coin` | gold coin | yes | "You flip the coin. It comes up 'still underground.'" |
| `book` | east | `book` | leather book | yes | "The pages are filled with inscrutable diagrams. You feel no smarter." |
| `scroll` | east | `scroll` | torn scroll | yes | "The scroll crumbles a little more in your hands. Great job." |
| `skeleton_key` | west | `key` | skeleton key | yes | "You hold up the key dramatically. Nothing responds to your drama." |
| `bell_rope` | up | `rope` | frayed rope | no | `None` — triggers cross-room effect; `use_response` is never reached |
| `skull` | down | `skull` | carved skull | yes | "You hold the skull up and contemplate mortality. It contemplates you back." |
| `amulet` | alcove | `amulet` | tarnished amulet | yes | "The amulet grows warm for a moment, then cold. Weird." |
| `journal` | cell | `journal` | prisoner's journal | yes | "You flip through it. The last entry just says 'DON'T PULL THE LEVER' over and over." |

Aliases: `sword` → `["blade"]`, `key` → `["skeletonkey"]`, `journal` → `["diary"]`

**Note on `use_response` for effect-triggering objects:** The `lever` and
`bell_rope` have `use_response = None` because the `use` dispatch always
finds a matching CrossRoomEffect first. The effect system handles all
messaging (including repeat-use messages). The `use_response` field is
dead data on these objects and is set to `None` for clarity.

### Doors (2)

| ID | Room | Noun | Display Name | Direction | Leads to | Starts | Player Operable | Opened/Unlocked by |
|----|------|------|-------------|-----------|----------|--------|-----------------|-------------------|
| `iron_grate` | down | `grate` | iron grate | south | `alcove` (The Hidden Alcove) | locked + closed | **no** | lever in cistern (cross-room effect toggles is_open) |
| `oak_door` | west | `door` | oak door | west | `cell` (The Abandoned Cell) | locked + closed | **yes** (once unlocked) | bell rope in bell tower (cross-room effect sets is_locked=False). Player then does `open door`. |

### Cross-Room Effects (2)

1. **Lever → Grate:** `use lever` in The Cistern → toggles `iron_grate.is_open`
   in The Crypt. `toggle=True`.
   - Open message: *"A grinding echo reverberates from deep below..."*
   - Close message: *"The grinding returns — something slides shut far beneath you."*
2. **Bell Rope → Oak Door:** `use rope` in The Bell Tower → sets
   `oak_door.is_locked = False` in The Cell Block. `toggle=False` (one-shot).
   - Message: *"The bell's toll shakes dust from the ceiling. Somewhere below, something heavy shifts..."*
   - Using the rope again after unlock: *"The bell rings again. Nothing new happens. You're just making noise now."*

---

## Test Strategy

Test runner: **pytest** (the `.gitignore` already includes `.pytest_cache/`).

### Unit Tests
- **Parser:** Input string → `ParseResult` or `None`. Cover:
  - One-word commands (`look`, `inventory`, `quit`, `north`, `n`)
  - Two-word commands (`go north`, `take sword`, `examine key`)
  - Verb aliases (`get` → `take`, `x` → `examine`, `l` → `look`)
  - Direction shortcuts (`n` → `go north`)
  - Error cases (empty, too many words, too long, unknown verb)
- **Command dispatch:** `GameState` + `ParseResult` → mutated `GameState`. Cover:
  - Movement (valid exit, invalid exit)
  - Take/drop (takeable, not takeable, not in room, not in inventory)
  - Open/close doors (locked, unlocked, already open, not player_operable)
  - Use with cross-room effect
  - Use without effect (check snarky response)
  - Object resolution (noun, alias, not found)

### Integration Tests
- Scripted playthrough: start at hub → go south → use lever → go hub → go
  down → verify grate is open and south exit exists
- Scripted playthrough: start at hub → go up → use rope → go hub → go west →
  open door → verify exit exists

### What NOT to test
- Specific error message text (random pool makes this brittle)
- Room/object description prose

---

## Out of Scope
- Save/load
- Combat
- Lighting/darkness
- Win/lose conditions
- Container objects
- Multi-word noun parsing (nouns are single words; display names are for output only)
- NPC interaction
- Timed events
- Colored terminal output
- External data files

---

## Design → Spec Traceability

| Design Decision | Spec Section | Status |
|----------------|-------------|--------|
| Three input patterns (0/1/2 word) | Parser: Token Patterns | Covered |
| No three-word commands | Parser: Token Patterns | Covered |
| Supported verbs (go, take, drop, look, examine, open, close, use, inventory, quit) | Command Dispatch table | Covered |
| `look` no-arg = room, `look noun` = examine synonym | Command Dispatch table | Covered |
| `examine` no-arg = error | Command Dispatch table | Covered |
| `use` is one-arg, context-free | `use` Dispatch section | Covered |
| `quit` with snarky confirmation | Command Dispatch table | Covered |
| 9 rooms, hub + 6 directional + 2 hidden | Room Map + Content Spec | Covered |
| 2 bridge passages, bidirectional, always open | Room Map | Covered |
| Verbose first visit / short revisit | Room Entry section | Covered |
| Fantasy dungeon theme | Content Spec: Theme | Covered |
| 2 cross-room effects, boolean, no chaining | CrossRoomEffect model + Content Spec | Covered |
| Simple cause-and-effect allowed, no multi-step chains | Door states + Cross-Room Effects | Covered |
| 10-12 objects, mix of takeable/stationary | Content Spec: Objects (12 listed) | Covered |
| Empty rooms allowed | Content Spec | Covered |
| Inventory, no weight/capacity | GameState model | Covered |
| Doors only, no containers | Door model + Open/Close Dispatch | Covered |
| Snarky parser errors | Error Messages section | Covered |
| No save/load, no combat | Out of Scope | Covered |
