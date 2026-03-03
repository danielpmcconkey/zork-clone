"""Room definitions and map layout."""

from zork.game import Room


def build_rooms() -> dict[str, Room]:
    rooms = {
        "hub": Room(
            id="hub",
            name="The Crossroads",
            description=(
                "You stand at the center of a vast underground chamber. Passages lead "
                "in every direction — north, south, east, west — and a staircase spirals "
                "both upward and downward. The air smells of dust and old decisions."
            ),
            short_description="The central chamber. Passages in every direction.",
            exits={
                "north": "north",
                "south": "south",
                "east": "east",
                "west": "west",
                "up": "up",
                "down": "down",
            },
            objects=["torch"],
        ),
        "north": Room(
            id="north",
            name="The Armory",
            description=(
                "Empty weapon racks line the walls, their contents long since looted. "
                "A few bent nails and a suspicious stain on the floor are all that remain "
                "of whatever battle was fought over these spoils. A narrow crawlspace leads west."
            ),
            short_description="An empty armory. Weapon racks gather dust. A crawlspace leads west.",
            exits={
                "south": "hub",
                "west": "west",
            },
            objects=["sword", "shield"],
        ),
        "south": Room(
            id="south",
            name="The Cistern",
            description=(
                "Water drips steadily into a shallow underground pool. The sound echoes "
                "off damp stone walls, making it impossible to tell which direction is which. "
                "An iron lever is mounted on the far wall."
            ),
            short_description="An underground pool. Drip. Drip. Drip.",
            exits={
                "north": "hub",
            },
            objects=["lever", "coin"],
        ),
        "east": Room(
            id="east",
            name="The Library",
            description=(
                "Collapsed bookshelves lean against each other like drunken scholars. "
                "Torn pages carpet the floor. Whatever knowledge was stored here has been "
                "thoroughly scattered. A crumbling spiral staircase descends into darkness."
            ),
            short_description="A ruined library. Books everywhere. A spiral staircase descends.",
            exits={
                "west": "hub",
                "down": "down",
            },
            objects=["book", "scroll"],
        ),
        "west": Room(
            id="west",
            name="The Cell Block",
            description=(
                "Rows of rusted iron bars divide the corridor into cramped cells. "
                "Old bones and scraps of cloth litter the floor. Something scratches "
                "faintly behind one of the walls. A narrow crawlspace leads east to the north."
            ),
            short_description="Rusted cells and old bones. A crawlspace leads to the north.",
            exits={
                "east": "hub",
                "north": "north",
            },
            objects=["skeleton_key"],
        ),
        "up": Room(
            id="up",
            name="The Bell Tower",
            description=(
                "Rickety wooden stairs spiral up to a small platform where a cracked "
                "bronze bell hangs from a rotting beam. A frayed rope dangles from the "
                "bell's clapper. The view through the broken slats is just more rock."
            ),
            short_description="A cracked bell hangs overhead. A rope dangles from it.",
            exits={
                "down": "hub",
            },
            objects=["bell_rope"],
        ),
        "down": Room(
            id="down",
            name="The Crypt",
            description=(
                "Stone sarcophagi line the walls in neat rows, their lids slightly ajar. "
                "The air is noticeably colder here. Frost clings to the edges of the stone. "
                "A crumbling spiral staircase leads up to the east."
            ),
            short_description="Cold stone tombs. Frost on everything. A staircase leads east.",
            exits={
                "up": "hub",
                "east": "east",
            },
            objects=["skull"],
        ),
        "alcove": Room(
            id="alcove",
            name="The Hidden Alcove",
            description=(
                "A tiny chamber barely large enough to stand in. Something glints in the "
                "dust — years of neglect have buried a small treasure beneath a layer of grime."
            ),
            short_description="A cramped alcove. Something glints in the dust.",
            exits={
                "north": "down",
            },
            objects=["amulet"],
        ),
        "cell": Room(
            id="cell",
            name="The Abandoned Cell",
            description=(
                "Scratches cover every inch of the walls — tally marks, mostly, but "
                "some are words. A pile of rags in the corner might have been a bed once. "
                "Whoever was kept here had a lot of time and very little hope."
            ),
            short_description="Scratched walls and a pile of rags. Grim.",
            exits={
                "east": "west",
            },
            objects=["journal"],
        ),
    }
    return rooms
