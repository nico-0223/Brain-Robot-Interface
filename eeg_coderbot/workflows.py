"""High-level workflows that orchestrate Cortex and CoderBot clients."""

from __future__ import annotations

import time
from typing import Any

from .coderbot import CoderBotClient
from .config import AppConfig
from .cortex import CortexClient
from .mental_states import MentalStateAlgorithm, get_algorithm
from .metrics import should_move_from_met_values, values_to_dict

AVAILABLE_STREAMS = ("eeg", "met", "mot", "dev", "eq", "pow", "com", "fac", "sys")


def prepare_session(cortex: CortexClient, include_license: bool = False) -> tuple[str, str]:
    """Authorize Cortex, select the first headset, and open a session."""

    print(f"User Login: {cortex.get_user_login()}\n")
    cortex.request_access()
    print("Access granted\n")
    token = cortex.get_token()
    if include_license:
        print(f"User License: {cortex.get_license_info(token)}\n")
    headset_id = cortex.get_first_headset_id()
    session_id = cortex.create_session(token, headset_id)
    return token, session_id


def subscribe_to_stream(config: AppConfig, stream_input: str, message_count: int = 100) -> None:
    """Subscribe to one Cortex stream and print received messages."""

    cortex = CortexClient(config.cortex)
    try:
        cortex.connect()
        token, session_id = prepare_session(cortex, include_license=True)
        response = cortex.subscribe(token, session_id, [stream_input])
        print(f"Subscription response: {response}\n")
        for _ in range(message_count):
            start = time.time()
            message = cortex.recv_json()
            print(f"Subscription: {message}\n")
            print(f"It took {time.time() - start} seconds!\n")
    finally:
        cortex.close()


def subscribe_metrics_and_control(config: AppConfig) -> None:
    """Subscribe to performance metrics and move CoderBot when criteria match."""

    cortex = CortexClient(config.cortex)
    coderbot = CoderBotClient(config.coderbot)
    try:
        cortex.connect()
        token, session_id = prepare_session(cortex)
        response = cortex.subscribe(token, session_id, ["met"])
        columns = response["result"]["success"][0]["cols"]
        stream_metrics_to_coderbot(
            cortex=cortex,
            coderbot=coderbot,
            columns=columns,
            stream_name="met",
            speed=config.movement.speed,
            elapse=config.movement.elapse,
            experiment_seconds=config.movement.experiment_seconds,
        )
    finally:
        cortex.close()


def stream_metrics_to_coderbot(
    cortex: CortexClient,
    coderbot: CoderBotClient,
    columns: list[str],
    stream_name: str,
    speed: int,
    elapse: int,
    experiment_seconds: float,
) -> None:
    """Process metric stream messages and delegate movement decisions."""

    start = time.time()
    while True:
        message: dict[str, Any] = cortex.recv_json()
        values = message[stream_name]
        metric_dict = values_to_dict(columns, values)
        print(f": Subscription : {metric_dict}\n")
        if len(values) <= 1 or values[1] is None:
            print("Nessun segnale. Controlla la qualità")
        elif should_move_from_met_values(values):
            coderbot.move(speed=speed, elapse=elapse)
        if time.time() - start > experiment_seconds:
            break


def subscribe_mental_state_algorithm(config: AppConfig, algorithm_name: str) -> None:
    """Run one mental-state algorithm against its Emotiv stream and control CoderBot."""

    algorithm = get_algorithm(algorithm_name)
    cortex = CortexClient(config.cortex)
    coderbot = CoderBotClient(config.coderbot)
    try:
        cortex.connect()
        token, session_id = prepare_session(cortex)
        response = cortex.subscribe(token, session_id, [algorithm.stream_name])
        columns = response["result"]["success"][0]["cols"]
        stream_mental_states_to_coderbot(
            cortex=cortex,
            coderbot=coderbot,
            algorithm=algorithm,
            columns=columns,
            experiment_seconds=config.movement.experiment_seconds,
        )
    finally:
        cortex.close()


def stream_mental_states_to_coderbot(
    cortex: CortexClient,
    coderbot: CoderBotClient,
    algorithm: MentalStateAlgorithm,
    columns: list[str],
    experiment_seconds: float,
) -> None:
    """Process Emotiv-classified mental states and execute mapped CoderBot moves."""

    start = time.time()
    while True:
        message: dict[str, Any] = cortex.recv_json()
        values = message[algorithm.stream_name]
        action = algorithm.evaluate(columns, values)
        print(
            f"Mental state ({algorithm.name}): {action.event.state} "
            f"confidence={action.event.confidence} raw={action.event.raw}\n"
        )
        if action.movement is not None:
            print(f"CoderBot movement selected: {action.movement.reason}\n")
            coderbot.move(speed=action.movement.speed, elapse=action.movement.elapse)
        if time.time() - start > experiment_seconds:
            break
