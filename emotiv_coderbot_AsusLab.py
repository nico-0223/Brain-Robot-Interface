"""Compatibility wrapper for the Emotiv metrics to CoderBot workflow."""

import sys

from eeg_coderbot.cli import main


if __name__ == "__main__":
    main(["coderbot", *sys.argv[1:]])
