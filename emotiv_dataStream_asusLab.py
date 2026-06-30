"""Compatibility wrapper for the general Emotiv data-stream workflow."""

import sys

from eeg_coderbot.cli import main


if __name__ == "__main__":
    main(["stream", *sys.argv[1:]])
