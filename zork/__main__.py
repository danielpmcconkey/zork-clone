"""Entry point: python -m zork"""

import logging
import sys

from zork.game import build_initial_state, describe_room, dispatch
from zork.parser import parse

WELCOME_BANNER = """\
ZORK CLONE
A cheap and dirty tribute to the classics.
Type 'help' to... just kidding. There is no help.
Type 'look' to look around.
"""


def main():
    if "--debug" in sys.argv:
        logging.basicConfig(
            level=logging.DEBUG,
            stream=sys.stderr,
            format="[DEBUG] %(message)s",
        )

    state = build_initial_state()
    print(WELCOME_BANNER)
    print(describe_room(state))

    while state.running:
        try:
            raw = input("> ")

            # Handle pending quit confirmation
            if state.pending_quit:
                if raw.strip().lower() in ("y", "yes"):
                    print("Fine. Be that way.")
                    state.running = False
                    break
                else:
                    print("Changed your mind? Good. The dungeon isn't done with you yet.")
                    state.pending_quit = False
                    continue

            result = parse(raw)
            if result is None:
                continue

            output = dispatch(state, result)
            print(output)

        except (KeyboardInterrupt, EOFError):
            print("\nFleeing so soon? Until next time...")
            break
        except Exception:
            logging.exception("Unexpected error during dispatch")
            print("Something went wrong. The dungeon shudders, then stabilizes.")
            continue


if __name__ == "__main__":
    main()
