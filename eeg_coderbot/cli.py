"""Command-line entrypoints for repository scripts."""

from __future__ import annotations

import argparse

from .config import AppConfig
from .mental_states import list_algorithms
from .workflows import (
    AVAILABLE_STREAMS,
    subscribe_mental_state_algorithm,
    subscribe_metrics_and_control,
    subscribe_to_stream,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emotiv Cortex and CoderBot utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stream_parser = subparsers.add_parser("stream", help="Subscribe to and print a Cortex stream")
    stream_parser.add_argument("--stream", choices=AVAILABLE_STREAMS, help="Cortex stream to subscribe to")
    stream_parser.add_argument("--message-count", type=int, default=100, help="Number of messages to print")

    subparsers.add_parser("coderbot", help="Subscribe to metrics and control CoderBot")

    mental_parser = subparsers.add_parser(
        "mental-states",
        help="Run a mental-state algorithm based on Emotiv-classified streams",
    )
    mental_parser.add_argument(
        "--algorithm",
        choices=list_algorithms(),
        default="performance-threshold",
        help="Mental-state reading algorithm to run",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = AppConfig.from_env()
    if args.command == "stream":
        stream = args.stream or input_stream_name()
        subscribe_to_stream(config, stream, message_count=args.message_count)
    elif args.command == "coderbot":
        subscribe_metrics_and_control(config)
    elif args.command == "mental-states":
        subscribe_mental_state_algorithm(config, args.algorithm)


def input_stream_name() -> str:
    prompt = (
        "Available data stream:\n\n"
        "'eeg' for EEG, 'met' for performance metrics, 'mot' for motion, 'dev' for device information,\n\n"
        "'eq' for EEG quality, 'pow' for the power of EEG data, 'com' for mental command,\n\n"
        "'fac' for facial expression, 'sys' for training of mental commands and facial expressions.\n\n"
        "Type requested data stream: "
    )
    return input(prompt)


if __name__ == "__main__":
    main()
