"""Compatibility wrapper for Emotiv mental-state algorithms controlling CoderBot."""

import sys

from eeg_coderbot.cli import main


if __name__ == "__main__":
    main(["mental-states", *sys.argv[1:]])
