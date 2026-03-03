"""Input parser. Turns raw text into ParseResult or None."""

from __future__ import annotations

from dataclasses import dataclass

from zork.errors import get_error

DIRECTIONS = {"north", "south", "east", "west", "up", "down"}
DIR_SHORTCUTS = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "u": "up", "d": "down",
}
VERB_ALIASES = {"get": "take", "x": "examine"}


@dataclass
class ParseResult:
    verb: str
    noun: str | None


def parse(raw: str) -> ParseResult | None:
    """Parse raw input into a command. Prints error and returns None on failure."""

    # Strip, lowercase
    text = raw.strip().lower()

    # Reject >256 chars
    if len(text) > 256:
        print(get_error("too_long"))
        return None

    # Strip non-printable chars (< ASCII 32)
    text = "".join(ch for ch in text if ord(ch) >= 32)

    # Empty check
    if not text:
        print(get_error("empty_input"))
        return None

    tokens = text.split()

    # Too many words
    if len(tokens) > 2:
        print(get_error("too_many_words"))
        return None

    if len(tokens) == 1:
        word = tokens[0]

        # Direction shortcuts: n/s/e/w/u/d
        if word in DIR_SHORTCUTS:
            return ParseResult("go", DIR_SHORTCUTS[word])

        # Full direction names
        if word in DIRECTIONS:
            return ParseResult("go", word)

        # Single-word commands
        if word == "i" or word == "inventory":
            return ParseResult("inventory", None)
        if word == "l" or word == "look":
            return ParseResult("look", None)
        if word == "q" or word == "quit":
            return ParseResult("quit", None)

        # Unknown single word
        print(get_error("unknown_verb", word=word))
        return None

    # Two tokens
    verb, noun = tokens

    # Verb aliases
    if verb in VERB_ALIASES:
        verb = VERB_ALIASES[verb]

    # 'l noun' -> 'look noun'
    if verb == "l":
        verb = "look"

    return ParseResult(verb, noun)
