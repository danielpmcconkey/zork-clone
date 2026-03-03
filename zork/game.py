"""Game state, data models, command dispatch, and helpers."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from zork.errors import get_error

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Room:
    id: str
    name: str
    description: str
    short_description: str
    exits: dict[str, str]
    objects: list[str]
    visited: bool = False


@dataclass
class GameObject:
    id: str
    noun: str
    display_name: str
    description: str
    takeable: bool
    use_response: str | None
    aliases: list[str] = field(default_factory=list)


@dataclass
class Door:
    id: str
    noun: str
    display_name: str
    description_open: str
    description_closed: str
    description_locked: str
    room_id: str
    direction: str
    target_room_id: str
    is_open: bool = False
    is_locked: bool = False
    player_operable: bool = True
    aliases: list[str] = field(default_factory=list)


@dataclass
class CrossRoomEffect:
    trigger_object_id: str
    trigger_action: str
    target_type: str
    target_id: str
    target_attribute: str
    target_value: bool
    message: str
    reverse_message: str = ""
    already_applied_message: str = ""
    toggle: bool = False


@dataclass
class GameState:
    rooms: dict[str, Room]
    objects: dict[str, GameObject]
    doors: dict[str, Door]
    effects: list[CrossRoomEffect]
    inventory: list[str]
    current_room: str
    running: bool = True
    pending_quit: bool = False


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def build_initial_state() -> GameState:
    from zork.rooms import build_rooms
    from zork.objects import build_objects, build_doors, build_effects

    return GameState(
        rooms=build_rooms(),
        objects=build_objects(),
        doors=build_doors(),
        effects=build_effects(),
        inventory=[],
        current_room="hub",
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_noun(state: GameState, noun: str) -> GameObject | Door | None:
    """Resolve a noun to an object or door. Search order per spec."""
    room = state.rooms[state.current_room]

    # 1. Objects in current room
    for obj_id in room.objects:
        obj = state.objects[obj_id]
        if obj.noun == noun or noun in obj.aliases:
            return obj

    # 2. Objects in inventory
    for obj_id in state.inventory:
        obj = state.objects[obj_id]
        if obj.noun == noun or noun in obj.aliases:
            return obj

    # 3. Doors in current room
    for door in state.doors.values():
        if door.room_id == state.current_room:
            if door.noun == noun or noun in door.aliases:
                return door

    return None


def describe_room(state: GameState, force_verbose: bool = False) -> str:
    """Build room description string. force_verbose=True for explicit 'look'."""
    room = state.rooms[state.current_room]
    parts = []

    parts.append(room.name)

    if force_verbose or not room.visited:
        parts.append(room.description)
        room.visited = True
    else:
        parts.append(room.short_description)

    # List objects
    for obj_id in room.objects:
        obj = state.objects[obj_id]
        article = "an" if obj.display_name[0].lower() in "aeiou" else "a"
        parts.append(f"There is {article} {obj.display_name} here.")

    # List doors
    for door in state.doors.values():
        if door.room_id == state.current_room:
            if door.is_open:
                parts.append(f"An open {door.display_name} leads {door.direction}.")
            else:
                parts.append(f"A closed {door.display_name} blocks the way {door.direction}.")

    # List exits
    exit_dirs = list(room.exits.keys())
    if exit_dirs:
        parts.append(f"Exits: {', '.join(exit_dirs)}")

    return "\n".join(parts)


def apply_effect(state: GameState, effect: CrossRoomEffect) -> str:
    """Apply a cross-room effect. Returns the message to display."""
    if effect.target_type == "door":
        target = state.doors[effect.target_id]
    else:
        target = state.objects[effect.target_id]

    current_value = getattr(target, effect.target_attribute)

    if effect.toggle:
        if current_value == effect.target_value:
            # Already in target state — reverse it
            setattr(target, effect.target_attribute, not effect.target_value)
            log.debug("Effect toggled %s.%s to %s", effect.target_id, effect.target_attribute, not effect.target_value)
            # If it's a door and we changed is_open, update exits
            if effect.target_type == "door" and effect.target_attribute == "is_open":
                _update_door_exits(state, target)
            return effect.reverse_message or effect.message
        else:
            # Apply it
            setattr(target, effect.target_attribute, effect.target_value)
            log.debug("Effect applied %s.%s to %s", effect.target_id, effect.target_attribute, effect.target_value)
            if effect.target_type == "door" and effect.target_attribute == "is_open":
                _update_door_exits(state, target)
            return effect.message
    else:
        # Non-toggle: check if already applied
        if current_value == effect.target_value:
            log.debug("Effect already applied for %s", effect.target_id)
            return effect.already_applied_message or effect.message
        else:
            setattr(target, effect.target_attribute, effect.target_value)
            log.debug("Effect applied %s.%s to %s", effect.target_id, effect.target_attribute, effect.target_value)
            if effect.target_type == "door" and effect.target_attribute == "is_open":
                _update_door_exits(state, target)
            return effect.message


def _update_door_exits(state: GameState, door: Door) -> None:
    """Add or remove exits when a door opens/closes."""
    room = state.rooms[door.room_id]
    target_room = state.rooms[door.target_room_id]

    if door.is_open:
        room.exits[door.direction] = door.target_room_id
        # Reverse direction
        reverse = _reverse_direction(door.direction)
        target_room.exits[reverse] = door.room_id
    else:
        room.exits.pop(door.direction, None)
        reverse = _reverse_direction(door.direction)
        target_room.exits.pop(reverse, None)


def _reverse_direction(direction: str) -> str:
    """Get the opposite direction."""
    opposites = {
        "north": "south", "south": "north",
        "east": "west", "west": "east",
        "up": "down", "down": "up",
    }
    return opposites.get(direction, direction)


# ---------------------------------------------------------------------------
# Command dispatch
# ---------------------------------------------------------------------------

def dispatch(state: GameState, cmd) -> str:
    """Dispatch a parsed command. Returns the output string."""
    from zork.parser import ParseResult

    verb = cmd.verb
    noun = cmd.noun

    log.debug("Dispatch: verb=%s noun=%s", verb, noun)

    if verb == "inventory":
        return _do_inventory(state)
    elif verb == "look" and noun is None:
        return describe_room(state, force_verbose=True)
    elif verb == "look" and noun is not None:
        return _do_examine(state, noun)
    elif verb == "quit":
        return _do_quit(state)
    elif verb == "go":
        return _do_go(state, noun)
    elif verb == "examine":
        if noun is None:
            return get_error("examine_nothing")
        return _do_examine(state, noun)
    elif verb == "take":
        return _do_take(state, noun)
    elif verb == "drop":
        return _do_drop(state, noun)
    elif verb == "use":
        return _do_use(state, noun)
    elif verb == "open":
        return _do_open(state, noun)
    elif verb == "close":
        return _do_close(state, noun)
    else:
        return get_error("unknown_verb", word=verb)


def _do_inventory(state: GameState) -> str:
    if not state.inventory:
        return "You're carrying nothing."
    items = [state.objects[oid].display_name for oid in state.inventory]
    return "You're carrying:\n" + "\n".join(f"  {name}" for name in items)


def _do_quit(state: GameState) -> str:
    state.pending_quit = True
    return "Are you sure you want to quit? (y/n)"


def _do_go(state: GameState, direction: str) -> str:
    room = state.rooms[state.current_room]
    if direction not in room.exits:
        return get_error("no_exit")

    state.current_room = room.exits[direction]
    log.debug("Moved to %s", state.current_room)
    return describe_room(state)


def _do_examine(state: GameState, noun: str) -> str:
    target = resolve_noun(state, noun)
    if target is None:
        return get_error("unknown_noun")
    if isinstance(target, Door):
        if target.is_open:
            return target.description_open
        else:
            return target.description_closed
    return target.description


def _do_take(state: GameState, noun: str) -> str:
    room = state.rooms[state.current_room]

    # Must be in the room (not inventory, not a door)
    target = None
    for obj_id in room.objects:
        obj = state.objects[obj_id]
        if obj.noun == noun or noun in obj.aliases:
            target = obj
            break

    if target is None:
        # Check if it's in inventory already
        for obj_id in state.inventory:
            obj = state.objects[obj_id]
            if obj.noun == noun or noun in obj.aliases:
                return "You're already carrying that."
        # Check if it's a door
        for door in state.doors.values():
            if door.room_id == state.current_room:
                if door.noun == noun or noun in door.aliases:
                    return get_error("cant_take")
        return get_error("unknown_noun")

    if not target.takeable:
        return get_error("cant_take")

    room.objects.remove(target.id)
    state.inventory.append(target.id)
    log.debug("Took %s", target.id)
    return f"Taken: {target.display_name}"


def _do_drop(state: GameState, noun: str) -> str:
    target = None
    for obj_id in state.inventory:
        obj = state.objects[obj_id]
        if obj.noun == noun or noun in obj.aliases:
            target = obj
            break

    if target is None:
        return get_error("cant_drop")

    state.inventory.remove(target.id)
    room = state.rooms[state.current_room]
    room.objects.append(target.id)
    log.debug("Dropped %s", target.id)
    return f"Dropped: {target.display_name}"


def _do_use(state: GameState, noun: str) -> str:
    target = resolve_noun(state, noun)
    if target is None:
        return get_error("unknown_noun")

    # Check effects list for a match
    for effect in state.effects:
        if effect.trigger_object_id == target.id and effect.trigger_action == "use":
            return apply_effect(state, effect)

    # No effect match — use the object's use_response or generic snark
    if isinstance(target, Door):
        return get_error("no_use")
    if target.use_response:
        return target.use_response
    return get_error("no_use")


def _do_open(state: GameState, noun: str) -> str:
    # Must resolve to a door
    target = resolve_noun(state, noun)
    if target is None:
        return get_error("unknown_noun")
    if not isinstance(target, Door):
        return get_error("not_operable")

    if not target.player_operable:
        return get_error("not_operable")
    if target.is_locked:
        return target.description_locked
    if target.is_open:
        return get_error("already_open")

    target.is_open = True
    _update_door_exits(state, target)
    log.debug("Opened %s", target.id)
    return f"You open the {target.display_name}."


def _do_close(state: GameState, noun: str) -> str:
    target = resolve_noun(state, noun)
    if target is None:
        return get_error("unknown_noun")
    if not isinstance(target, Door):
        return get_error("not_operable")

    if not target.player_operable:
        return get_error("not_operable")
    if not target.is_open:
        return get_error("already_closed")

    target.is_open = False
    _update_door_exits(state, target)
    log.debug("Closed %s", target.id)
    return f"You close the {target.display_name}."
