"""Game dispatch unit tests."""

from zork.game import (
    build_initial_state,
    dispatch,
    resolve_noun,
    describe_room,
    GameState,
    Door,
    GameObject,
)
from zork.parser import ParseResult


def fresh_state() -> GameState:
    return build_initial_state()


# --- Movement ---

def test_move_valid_exit():
    state = fresh_state()
    assert state.current_room == "hub"
    dispatch(state, ParseResult("go", "north"))
    assert state.current_room == "north"


def test_move_invalid_exit():
    state = fresh_state()
    # hub has no "northwest" exit
    result = dispatch(state, ParseResult("go", "northwest"))
    assert state.current_room == "hub"
    assert len(result) > 0  # got an error message


# --- Take ---

def test_take_takeable_object():
    state = fresh_state()
    assert "torch" in state.rooms["hub"].objects
    result = dispatch(state, ParseResult("take", "torch"))
    assert "torch" not in state.rooms["hub"].objects
    assert "torch" in state.inventory
    assert "Taken" in result


def test_take_non_takeable():
    state = fresh_state()
    state.current_room = "south"
    result = dispatch(state, ParseResult("take", "lever"))
    assert "lever" in state.rooms["south"].objects
    assert "lever" not in state.inventory


def test_take_object_not_in_room():
    state = fresh_state()
    # sword is in north, not hub
    result = dispatch(state, ParseResult("take", "sword"))
    assert "sword" not in state.inventory


# --- Drop ---

def test_drop_from_inventory():
    state = fresh_state()
    # Take torch first
    dispatch(state, ParseResult("take", "torch"))
    assert "torch" in state.inventory
    result = dispatch(state, ParseResult("drop", "torch"))
    assert "torch" not in state.inventory
    assert "torch" in state.rooms["hub"].objects
    assert "Dropped" in result


def test_drop_not_in_inventory():
    state = fresh_state()
    result = dispatch(state, ParseResult("drop", "sword"))
    assert len(result) > 0  # error message


# --- Examine ---

def test_examine_object_in_room():
    state = fresh_state()
    result = dispatch(state, ParseResult("examine", "torch"))
    assert "brass torch" in result.lower() or "torch" in result.lower()


def test_examine_object_in_inventory():
    state = fresh_state()
    dispatch(state, ParseResult("take", "torch"))
    result = dispatch(state, ParseResult("examine", "torch"))
    assert len(result) > 0


def test_examine_nothing():
    state = fresh_state()
    result = dispatch(state, ParseResult("examine", None))
    assert len(result) > 0  # error message


def test_examine_door():
    state = fresh_state()
    state.current_room = "down"
    result = dispatch(state, ParseResult("examine", "grate"))
    assert len(result) > 0


# --- Open / Close ---

def test_open_unlocked_door():
    state = fresh_state()
    state.current_room = "west"
    # Unlock the oak door first
    state.doors["oak_door"].is_locked = False
    result = dispatch(state, ParseResult("open", "door"))
    assert state.doors["oak_door"].is_open
    assert "west" in state.rooms["west"].exits
    assert "east" in state.rooms["cell"].exits


def test_open_locked_door():
    state = fresh_state()
    state.current_room = "west"
    result = dispatch(state, ParseResult("open", "door"))
    assert not state.doors["oak_door"].is_open
    assert "locked" in result.lower()


def test_open_not_player_operable():
    state = fresh_state()
    state.current_room = "down"
    result = dispatch(state, ParseResult("open", "grate"))
    assert not state.doors["iron_grate"].is_open


def test_open_already_open():
    state = fresh_state()
    state.current_room = "west"
    state.doors["oak_door"].is_locked = False
    state.doors["oak_door"].is_open = True
    result = dispatch(state, ParseResult("open", "door"))
    # Should get "already open" error


def test_close_open_door():
    state = fresh_state()
    state.current_room = "west"
    state.doors["oak_door"].is_locked = False
    # Open it
    dispatch(state, ParseResult("open", "door"))
    assert state.doors["oak_door"].is_open
    # Close it
    result = dispatch(state, ParseResult("close", "door"))
    assert not state.doors["oak_door"].is_open
    assert "west" not in state.rooms["west"].exits


# --- Use with effects ---

def test_use_lever_opens_grate():
    state = fresh_state()
    state.current_room = "south"
    result = dispatch(state, ParseResult("use", "lever"))
    assert state.doors["iron_grate"].is_open
    assert "south" in state.rooms["down"].exits
    assert "grinding" in result.lower()


def test_use_lever_toggles():
    state = fresh_state()
    state.current_room = "south"
    # Open
    dispatch(state, ParseResult("use", "lever"))
    assert state.doors["iron_grate"].is_open
    # Close
    result = dispatch(state, ParseResult("use", "lever"))
    assert not state.doors["iron_grate"].is_open
    assert "south" not in state.rooms["down"].exits


def test_use_rope_unlocks_door():
    state = fresh_state()
    state.current_room = "up"
    result = dispatch(state, ParseResult("use", "rope"))
    assert not state.doors["oak_door"].is_locked
    assert "bell" in result.lower()


def test_use_rope_again_no_change():
    state = fresh_state()
    state.current_room = "up"
    dispatch(state, ParseResult("use", "rope"))
    assert not state.doors["oak_door"].is_locked
    # Use again
    result = dispatch(state, ParseResult("use", "rope"))
    assert not state.doors["oak_door"].is_locked
    assert "noise" in result.lower()


def test_use_sword_snarky():
    state = fresh_state()
    state.current_room = "north"
    result = dispatch(state, ParseResult("use", "sword"))
    assert "darkness" in result.lower()


def test_use_generic_snark():
    state = fresh_state()
    # Torch has a use_response
    result = dispatch(state, ParseResult("use", "torch"))
    assert len(result) > 0


# --- Resolve noun ---

def test_resolve_by_noun():
    state = fresh_state()
    obj = resolve_noun(state, "torch")
    assert obj is not None
    assert obj.id == "torch"


def test_resolve_by_alias():
    state = fresh_state()
    state.current_room = "north"
    obj = resolve_noun(state, "blade")
    assert obj is not None
    assert obj.id == "sword"


def test_resolve_unknown():
    state = fresh_state()
    obj = resolve_noun(state, "unicorn")
    assert obj is None


def test_resolve_door():
    state = fresh_state()
    state.current_room = "down"
    obj = resolve_noun(state, "grate")
    assert obj is not None
    assert isinstance(obj, Door)
    assert obj.id == "iron_grate"


def test_resolve_door_alias():
    state = fresh_state()
    state.current_room = "down"
    obj = resolve_noun(state, "bars")
    assert obj is not None
    assert obj.id == "iron_grate"


# --- Inventory ---

def test_inventory_empty():
    state = fresh_state()
    result = dispatch(state, ParseResult("inventory", None))
    assert "nothing" in result.lower()


def test_inventory_with_items():
    state = fresh_state()
    dispatch(state, ParseResult("take", "torch"))
    result = dispatch(state, ParseResult("inventory", None))
    assert "brass torch" in result


# --- Look ---

def test_look_always_verbose():
    state = fresh_state()
    # Visit the room (mark visited)
    state.rooms["hub"].visited = True
    result = dispatch(state, ParseResult("look", None))
    # Should show full description even though visited=True
    assert "vast underground chamber" in result


# --- Describe room first vs revisit ---

def test_first_visit_verbose():
    state = fresh_state()
    assert not state.rooms["hub"].visited
    result = describe_room(state)
    assert "vast underground chamber" in result
    assert state.rooms["hub"].visited


def test_revisit_short():
    state = fresh_state()
    state.rooms["hub"].visited = True
    result = describe_room(state)
    assert "central chamber" in result.lower()


# --- Quit ---

def test_quit_sets_pending():
    state = fresh_state()
    result = dispatch(state, ParseResult("quit", None))
    assert state.pending_quit
    assert "sure" in result.lower()
