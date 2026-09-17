#!/usr/bin/env python3
"""Compatibility entry point for the current profile-card generator.

The project previously shipped two independent generators. Keeping this file as
an entry point avoids breaking existing commands while ensuring both commands
produce the same maintained output.
"""

from generate_card import main


if __name__ == "__main__":
    main()
