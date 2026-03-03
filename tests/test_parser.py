"""Parser unit tests."""

from zork.parser import parse, ParseResult


def test_go_north():
    result = parse("go north")
    assert result == ParseResult("go", "north")


def test_bare_north():
    result = parse("north")
    assert result == ParseResult("go", "north")


def test_shortcut_n():
    result = parse("n")
    assert result == ParseResult("go", "north")


def test_all_direction_shortcuts():
    for short, full in [("n", "north"), ("s", "south"), ("e", "east"),
                         ("w", "west"), ("u", "up"), ("d", "down")]:
        result = parse(short)
        assert result == ParseResult("go", full), f"Failed for {short}"


def test_all_bare_directions():
    for d in ["north", "south", "east", "west", "up", "down"]:
        result = parse(d)
        assert result == ParseResult("go", d), f"Failed for {d}"


def test_look_no_noun():
    assert parse("look") == ParseResult("look", None)


def test_look_shortcut():
    assert parse("l") == ParseResult("look", None)


def test_inventory():
    assert parse("inventory") == ParseResult("inventory", None)


def test_inventory_shortcut():
    assert parse("i") == ParseResult("inventory", None)


def test_quit():
    assert parse("quit") == ParseResult("quit", None)


def test_quit_shortcut():
    assert parse("q") == ParseResult("quit", None)


def test_take_sword():
    assert parse("take sword") == ParseResult("take", "sword")


def test_get_normalizes_to_take():
    assert parse("get sword") == ParseResult("take", "sword")


def test_examine_key():
    assert parse("examine key") == ParseResult("examine", "key")


def test_x_normalizes_to_examine():
    assert parse("x key") == ParseResult("examine", "key")


def test_look_with_noun():
    assert parse("l sword") == ParseResult("look", "sword")


def test_empty_input(capsys):
    assert parse("") is None
    captured = capsys.readouterr()
    assert len(captured.out.strip()) > 0


def test_too_many_words(capsys):
    assert parse("a b c") is None
    captured = capsys.readouterr()
    assert len(captured.out.strip()) > 0


def test_too_long(capsys):
    assert parse("x" * 300) is None
    captured = capsys.readouterr()
    assert len(captured.out.strip()) > 0


def test_unknown_verb(capsys):
    assert parse("flurble") is None
    captured = capsys.readouterr()
    assert len(captured.out.strip()) > 0


def test_case_insensitive():
    assert parse("GO NORTH") == ParseResult("go", "north")


def test_whitespace_stripping():
    assert parse("  look  ") == ParseResult("look", None)


def test_two_word_open():
    assert parse("open door") == ParseResult("open", "door")


def test_two_word_close():
    assert parse("close door") == ParseResult("close", "door")


def test_two_word_use():
    assert parse("use lever") == ParseResult("use", "lever")


def test_two_word_drop():
    assert parse("drop sword") == ParseResult("drop", "sword")
