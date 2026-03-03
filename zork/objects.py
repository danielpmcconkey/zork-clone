"""Object, door, and cross-room effect definitions."""

from zork.game import GameObject, Door, CrossRoomEffect


def build_objects() -> dict[str, GameObject]:
    objects = [
        GameObject(
            id="torch",
            noun="torch",
            display_name="brass torch",
            description="A heavy brass torch, still faintly warm. The flame died long ago, but the metal remembers.",
            takeable=True,
            use_response="You wave the torch around. Nothing happens, because this isn't that kind of game.",
        ),
        GameObject(
            id="sword",
            noun="sword",
            display_name="rusty sword",
            description="A sword that has seen better centuries. The blade is pitted with rust, but the edge could still give you tetanus.",
            takeable=True,
            use_response="You swing at the darkness. The darkness is unimpressed.",
            aliases=["blade"],
        ),
        GameObject(
            id="shield",
            noun="shield",
            display_name="dented shield",
            description="A shield bearing a coat of arms too corroded to identify. It's dented in a way that suggests its last owner had a bad day.",
            takeable=True,
            use_response="You raise the shield heroically. No one is watching.",
        ),
        GameObject(
            id="lever",
            noun="lever",
            display_name="iron lever",
            description="A heavy iron lever set into the wall. It looks functional, which is more than you can say for most things down here.",
            takeable=False,
            use_response=None,
        ),
        GameObject(
            id="coin",
            noun="coin",
            display_name="gold coin",
            description="A single gold coin, stamped with a face you don't recognize. Still shiny, though. Underground economics.",
            takeable=True,
            use_response="You flip the coin. It comes up 'still underground.'",
        ),
        GameObject(
            id="book",
            noun="book",
            display_name="leather book",
            description="A thick leather-bound tome. Most of the pages have been torn out, and the remaining ones are covered in diagrams that hurt to look at.",
            takeable=True,
            use_response="The pages are filled with inscrutable diagrams. You feel no smarter.",
        ),
        GameObject(
            id="scroll",
            noun="scroll",
            display_name="torn scroll",
            description="A scroll that's been torn nearly in half. What's left reads like instructions for something you'd rather not attempt.",
            takeable=True,
            use_response="The scroll crumbles a little more in your hands. Great job.",
        ),
        GameObject(
            id="skeleton_key",
            noun="key",
            display_name="skeleton key",
            description="An ornate skeleton key, blackened with age. The teeth are filed into an intricate pattern.",
            takeable=True,
            use_response="You hold up the key dramatically. Nothing responds to your drama.",
            aliases=["skeletonkey"],
        ),
        GameObject(
            id="bell_rope",
            noun="rope",
            display_name="frayed rope",
            description="A length of frayed rope hanging from the bell's clapper. One good pull should do it.",
            takeable=False,
            use_response=None,
        ),
        GameObject(
            id="skull",
            noun="skull",
            display_name="carved skull",
            description="A human skull with intricate carvings etched into the bone. The eye sockets seem to follow you. They don't, but they seem to.",
            takeable=True,
            use_response="You hold the skull up and contemplate mortality. It contemplates you back.",
        ),
        GameObject(
            id="amulet",
            noun="amulet",
            display_name="tarnished amulet",
            description="A small amulet on a corroded chain. The gemstone at its center is clouded but still faintly luminous.",
            takeable=True,
            use_response="The amulet grows warm for a moment, then cold. Weird.",
        ),
        GameObject(
            id="journal",
            noun="journal",
            display_name="prisoner's journal",
            description="A battered journal filled with increasingly frantic handwriting. The last few pages are just the same sentence repeated.",
            takeable=True,
            use_response="You flip through it. The last entry just says 'DON'T PULL THE LEVER' over and over.",
            aliases=["diary"],
        ),
    ]
    return {obj.id: obj for obj in objects}


def build_doors() -> dict[str, Door]:
    doors = [
        Door(
            id="iron_grate",
            noun="grate",
            display_name="iron grate",
            description_open="The iron grate stands open, revealing a dark passage to the south.",
            description_closed="A heavy iron grate blocks a passage to the south. It looks like it's operated by some mechanism.",
            description_locked="The grate is sealed tight. No keyhole, no handle — it must be controlled from somewhere else.",
            room_id="down",
            direction="south",
            target_room_id="alcove",
            is_open=False,
            is_locked=True,
            player_operable=False,
            aliases=["bars"],
        ),
        Door(
            id="oak_door",
            noun="door",
            display_name="oak door",
            description_open="The oak door stands open, revealing a cramped cell beyond.",
            description_closed="A sturdy oak door, banded with iron. There's a large keyhole, but it might not need a key.",
            description_locked="The oak door is locked. The mechanism looks old but solid. Maybe there's another way to open it.",
            room_id="west",
            direction="west",
            target_room_id="cell",
            is_open=False,
            is_locked=True,
            player_operable=True,
            aliases=["oak"],
        ),
    ]
    return {door.id: door for door in doors}


def build_effects() -> list[CrossRoomEffect]:
    return [
        CrossRoomEffect(
            trigger_object_id="lever",
            trigger_action="use",
            target_type="door",
            target_id="iron_grate",
            target_attribute="is_open",
            target_value=True,
            message="A grinding echo reverberates from deep below...",
            reverse_message="The grinding returns — something slides shut far beneath you.",
            toggle=True,
        ),
        CrossRoomEffect(
            trigger_object_id="bell_rope",
            trigger_action="use",
            target_type="door",
            target_id="oak_door",
            target_attribute="is_locked",
            target_value=False,
            message="The bell's toll shakes dust from the ceiling. Somewhere below, something heavy shifts...",
            already_applied_message="The bell rings again. Nothing new happens. You're just making noise now.",
            toggle=False,
        ),
    ]
