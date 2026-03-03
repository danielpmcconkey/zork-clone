"""Snarky error message pools. Classic Zork energy."""

import random

ERROR_POOLS: dict[str, list[str]] = {
    "unknown_verb": [
        "I don't know the word '{word}'. I don't know a lot of words, but that one especially.",
        "'{word}'? Is that even a word? I'm going to assume no.",
        "I've been trapped in this dungeon for centuries and I've never heard '{word}' before.",
    ],
    "unknown_noun": [
        "You don't see that here.",
        "I don't see anything like that. Are you hallucinating?",
        "Whatever you're looking for, it ain't here.",
    ],
    "cant_take": [
        "You can't take that. Believe me, I've tried.",
        "That's not the kind of thing you can just pick up.",
        "Yeah, that's not going anywhere. Neither are you, at this rate.",
    ],
    "cant_drop": [
        "You're not carrying that.",
        "Hard to drop something you don't have.",
        "Check your pockets again — nope, not there.",
    ],
    "no_exit": [
        "You can't go that way.",
        "There's nothing in that direction but solid rock and regret.",
        "That's a wall. Walls are famously impassable.",
    ],
    "already_open": [
        "It's already open. What more do you want?",
        "You already opened that. Short-term memory issues?",
        "Still open from last time. Doors don't close themselves. Well, some do. Not this one.",
    ],
    "already_closed": [
        "It's already closed.",
        "Can't close what's already closed. That's just... standing near a closed thing.",
        "It's shut. It was shut. It remains shut.",
    ],
    "no_use": [
        "You can't figure out how to use that.",
        "Using that accomplishes exactly nothing.",
        "You fiddle with it for a while. Nothing happens. You feel foolish.",
    ],
    "not_operable": [
        "It won't budge by hand.",
        "You push and pull. Nothing. Maybe there's another way.",
        "Your bare hands aren't going to cut it here.",
    ],
    "door_locked": [
        "It's locked tight.",
        "Locked. You'd need a miracle or a really specific game mechanic.",
        "That's locked. Brute force isn't one of your skills.",
    ],
    "empty_input": [
        "I'm not a mind reader. Well, I am, and your mind is blank.",
        "You stand silently. The dungeon judges you.",
        "Say something. Type something. Anything. Please.",
    ],
    "too_many_words": [
        "I'm a simple creature. Two words max.",
        "Whoa, slow down Shakespeare. Keep it to two words.",
        "This isn't a conversation. Verb noun. That's the deal.",
    ],
    "too_long": [
        "That input is longer than this entire dungeon. Keep it under 256 characters.",
        "I stopped reading after the first 256 characters. So should you.",
        "TL;DR — your input, I mean. Way too long.",
    ],
    "examine_nothing": [
        "Examine what, exactly?",
        "You stare intently at nothing in particular.",
        "You'll need to be more specific. 'examine' what?",
    ],
}


def get_error(category: str, **kwargs) -> str:
    """Pick a random error from the pool. Pass keyword args for formatting."""
    pool = ERROR_POOLS.get(category, ["Something went wrong. Don't ask me what."])
    msg = random.choice(pool)
    if kwargs:
        try:
            msg = msg.format(**kwargs)
        except KeyError:
            pass
    return msg
