"""Integration tests — scripted playthroughs."""

from zork.game import build_initial_state, dispatch
from zork.parser import parse


def run(state, cmd_str):
    """Helper: parse and dispatch a command string."""
    result = parse(cmd_str)
    assert result is not None, f"Parse failed for: {cmd_str}"
    return dispatch(state, result)


def test_lever_opens_grate_full_playthrough():
    """Lever in Cistern → opens iron grate in Crypt → walk into Alcove."""
    state = build_initial_state()
    assert state.current_room == "hub"

    # Go south to the Cistern
    run(state, "go south")
    assert state.current_room == "south"

    # Use the lever
    result = run(state, "use lever")
    assert "grinding" in result.lower()

    # Verify grate is open
    assert state.doors["iron_grate"].is_open

    # Go back to hub
    run(state, "go north")
    assert state.current_room == "hub"

    # Go down to the Crypt
    run(state, "go down")
    assert state.current_room == "down"

    # Verify south exit now exists
    assert "south" in state.rooms["down"].exits

    # Walk into the Hidden Alcove
    run(state, "go south")
    assert state.current_room == "alcove"

    # Walk back
    run(state, "go north")
    assert state.current_room == "down"


def test_bell_rope_unlocks_oak_door_full_playthrough():
    """Bell rope in Bell Tower → unlocks oak door in Cell Block → open and enter cell."""
    state = build_initial_state()
    assert state.current_room == "hub"

    # Go up to the Bell Tower
    run(state, "go up")
    assert state.current_room == "up"

    # Use the rope
    result = run(state, "use rope")
    assert "bell" in result.lower()

    # Verify door is unlocked
    assert not state.doors["oak_door"].is_locked

    # Go back to hub
    run(state, "go down")
    assert state.current_room == "hub"

    # Go west to the Cell Block
    run(state, "go west")
    assert state.current_room == "west"

    # Open the oak door (should be unlocked now)
    result = run(state, "open door")
    assert state.doors["oak_door"].is_open

    # Verify exit exists
    assert "west" in state.rooms["west"].exits

    # Walk into the Abandoned Cell
    run(state, "go west")
    assert state.current_room == "cell"

    # Walk back
    run(state, "go east")
    assert state.current_room == "west"


def test_lever_toggle_round_trip():
    """Lever opens grate, lever again closes grate."""
    state = build_initial_state()

    # Go south, use lever to open
    run(state, "go south")
    run(state, "use lever")
    assert state.doors["iron_grate"].is_open
    assert "south" in state.rooms["down"].exits

    # Use lever again to close
    result = run(state, "use lever")
    assert not state.doors["iron_grate"].is_open
    assert "south" not in state.rooms["down"].exits


def test_bridge_passage_east_down():
    """East room and Down room are connected via bridge passage."""
    state = build_initial_state()

    # Go east
    run(state, "go east")
    assert state.current_room == "east"

    # Go down from east (bridge to down room)
    run(state, "go down")
    assert state.current_room == "down"

    # Go east from down (bridge back to east)
    run(state, "go east")
    assert state.current_room == "east"


def test_bridge_passage_north_west():
    """North room and West room are connected via bridge passage."""
    state = build_initial_state()

    # Go north
    run(state, "go north")
    assert state.current_room == "north"

    # Go west from north (bridge to west)
    run(state, "go west")
    assert state.current_room == "west"

    # Go north from west (bridge back to north)
    run(state, "go north")
    assert state.current_room == "north"


def test_full_exploration():
    """Visit all 9 rooms via normal paths and puzzles."""
    state = build_initial_state()
    visited = set()

    def visit(cmd_str, expected_room):
        run(state, cmd_str)
        assert state.current_room == expected_room
        visited.add(expected_room)

    visited.add("hub")

    # Hub -> all 6 directions
    visit("go north", "north")
    visit("go south", "hub")  # back

    visit("go south", "south")
    # Solve lever puzzle while here
    run(state, "use lever")
    visit("go north", "hub")

    visit("go east", "east")
    visit("go west", "hub")

    visit("go west", "west")
    visit("go east", "hub")

    visit("go up", "up")
    # Solve bell rope puzzle while here
    run(state, "use rope")
    visit("go down", "hub")

    visit("go down", "down")
    visited.add("down")
    # Grate should be open, go south to alcove
    visit("go south", "alcove")
    visit("go north", "down")
    visit("go up", "hub")

    # Go west and open the oak door
    visit("go west", "west")
    run(state, "open door")
    visit("go west", "cell")

    assert visited == {"hub", "north", "south", "east", "west", "up", "down", "alcove", "cell"}
