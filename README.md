# EEG CoderBot Emotiv Integration

## Overview

This repository contains a small Python codebase for connecting to an Emotiv headset through the Emotiv Cortex WebSocket API, streaming EEG-related data, and optionally sending CoderBot movement commands from Emotiv performance metrics.

The project has been organized into reusable modules so the external API calls, configuration, workflow orchestration, and metric decision logic can be tested independently. The original script filenames are kept as compatibility entrypoints.

## Main purpose

The code supports three main workflows:

- Subscribe to an Emotiv Cortex data stream and print incoming messages.
- Subscribe to Emotiv performance metrics (`met`) and ask CoderBot to move when engagement and excitement values are both positive.
- Run a selectable mental-state reading algorithm that consumes Emotiv-classified Cortex streams and maps the resulting state to a CoderBot movement plan.

The repository appears to be exploratory or lab-oriented. It assumes that Emotiv Launcher/Cortex is running locally, that valid Emotiv application credentials are available, and that a compatible headset is connected.

## Repository structure

```text
.
├── eeg_coderbot/
│   ├── __init__.py            # Package exports
│   ├── cli.py                 # Command-line argument parsing and entrypoint routing
│   ├── coderbot.py            # CoderBot HTTP client, including dry-run behavior
│   ├── config.py              # Centralized environment-based configuration
│   ├── cortex.py              # Emotiv Cortex JSON-RPC WebSocket client
│   ├── metrics.py             # Reusable metric mapping and movement decision helpers
│   ├── mental_states/         # Emotiv-classified mental-state reading algorithms
│   └── workflows.py           # High-level Emotiv streaming and CoderBot orchestration
├── tests/
│   ├── test_coderbot.py       # Unit tests for CoderBot API and dry-run behavior
│   ├── test_config.py         # Unit tests for environment configuration parsing
│   └── test_metrics.py        # Unit tests for metric helpers and edge cases
├── .env.example               # Example environment configuration
├── emotiv_coderbot_AsusLab.py # Compatibility wrapper for metrics-to-CoderBot workflow
├── emotiv_dataStream_asusLab.py # Compatibility wrapper for stream-printing workflow
├── emotiv_mental_states_AsusLab.py # Compatibility wrapper for mental-state algorithms
├── requirements.txt           # Runtime Python dependencies
└── README.md                  # Project documentation
```

## Architecture

The code separates responsibilities into explicit modules:

- **Configuration**: `eeg_coderbot.config` reads environment variables into typed dataclasses.
- **External API calls**: `eeg_coderbot.cortex` wraps Emotiv Cortex WebSocket JSON-RPC calls, and `eeg_coderbot.coderbot` wraps CoderBot HTTP calls.
- **Business logic**: `eeg_coderbot.metrics` contains the reusable movement decision helper.
- **Mental-state algorithms**: `eeg_coderbot.mental_states` contains algorithms that consume Emotiv-classified `met` and `com` streams and map states to CoderBot movement plans.
- **Orchestration**: `eeg_coderbot.workflows` coordinates Cortex sessions, subscriptions, and CoderBot movement.
- **CLI/entrypoints**: `eeg_coderbot.cli` handles command-line routing. The original root scripts delegate to this CLI so existing usage still works.
- **Tests**: `tests/` covers configuration parsing, metric edge cases, and dry-run/API behavior without requiring real Emotiv or CoderBot services.

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd eeg_coderbot
```

### 2. Create and activate a Python environment

Python 3 is required. A virtual environment is recommended:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

The runtime dependencies are:

- `requests`
- `websockets`

The tests use Python's standard-library `unittest` framework, so no separate test dependency is required.

## Configuration and environment setup

Copy `.env.example` or export equivalent environment variables in your shell. The code reads from environment variables directly; it does not automatically load `.env` files.

```bash
cp .env.example .env
```

If you use a `.env` file, load it with your shell or preferred environment manager before running the scripts.

### Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `EMOTIV_CORTEX_URL` | `wss://localhost:6868` | Emotiv Cortex WebSocket URL. |
| `EMOTIV_CLIENT_ID` | empty | Emotiv application client ID. |
| `EMOTIV_CLIENT_SECRET` | empty | Emotiv application client secret. Do not commit real secrets. |
| `CODERBOT_BASE_URL` | empty | Base URL for the CoderBot HTTP API. Required for non-dry-run CoderBot actions. |
| `DRY_RUN` | `false` | When true, prints CoderBot actions without sending mutating HTTP requests. |
| `CODERBOT_MOVE_SPEED` | `100` | Speed value sent to the CoderBot movement endpoint. |
| `CODERBOT_MOVE_ELAPSE` | `1` | Duration value sent to the CoderBot movement endpoint. |
| `EXPERIMENT_SECONDS` | `120` | Duration of the metrics-to-CoderBot loop. |

### External services

You need the following for live runs:

- Emotiv Launcher / Cortex service running locally or at `EMOTIV_CORTEX_URL`
- An Emotiv headset connected and available through Cortex
- Valid Emotiv application credentials
- For CoderBot control, a reachable CoderBot HTTP API base URL

## Mental-state algorithms

Mental-state algorithms live in `eeg_coderbot/mental_states/`. They are based on Emotiv-classified stream data rather than raw EEG signal processing. Two algorithms are included:

| Algorithm | Emotiv stream | What it reads | CoderBot behavior |
| --- | --- | --- | --- |
| `performance-threshold` | `met` | Emotiv performance metrics such as engagement, excitement, relaxation, stress, interest, and focus. | Maps focused, relaxed, interested, and engaged/excited states to different `move` speeds/durations; stress, neutral, and no-signal states do not move. |
| `mental-command` | `com` | Emotiv mental-command action and power values. | Maps known actions such as `push`, `pull`, `lift`, `drop`, `left`, and `right` to different `move` speeds/durations when power is above threshold. Unknown or low-power commands do not move. |

Run the default algorithm with:

```bash
python emotiv_mental_states_AsusLab.py
```

Or select an algorithm explicitly:

```bash
python -m eeg_coderbot.cli mental-states --algorithm performance-threshold
python -m eeg_coderbot.cli mental-states --algorithm mental-command
```

The movement mappings intentionally use the existing CoderBot `move` command only, because the repository does not document additional movement endpoints such as turn or stop commands.

## Dry-run mode

Dry-run mode is controlled by `DRY_RUN=true`. In dry-run mode, the metrics-to-CoderBot workflow still connects to Emotiv Cortex and processes stream messages, but CoderBot mutating HTTP requests are not sent. Instead, the CoderBot client prints a visible message such as:

```text
DRY RUN: would POST http://coderbot.local/control/move with {'speed': 100, 'elapse': 1}
```

Use dry-run mode when testing the integration flow without moving a robot:

```bash
export DRY_RUN=true
python emotiv_coderbot_AsusLab.py
# or
python emotiv_mental_states_AsusLab.py
```

## How to run the code

### Stream Emotiv data

Run the compatibility script:

```bash
python emotiv_dataStream_asusLab.py
```

When prompted, enter one of the stream names shown by the script, for example:

```text
met
```

Alternatively, call the package CLI directly:

```bash
python -m eeg_coderbot.cli stream --stream met --message-count 100
```

The script will print subscription messages received from Cortex.

### Stream metrics and control CoderBot

After configuring Emotiv credentials and `CODERBOT_BASE_URL`, run:

```bash
python emotiv_coderbot_AsusLab.py
```

Or call the package CLI directly:

```bash
python -m eeg_coderbot.cli coderbot
```

To run the mental-state algorithm workflow, use:

```bash
python -m eeg_coderbot.cli mental-states --algorithm performance-threshold
```

The workflow subscribes to the `met` stream and monitors selected performance metrics. If engagement and excitement values are present and both greater than zero, it calls the CoderBot movement client.

In non-dry-run mode, that sends:

```http
POST {CODERBOT_BASE_URL}/control/move
```

with a JSON body similar to:

```json
{
  "speed": 100,
  "elapse": 1
}
```

## Example usage

Example workflow for printing the performance-metric stream:

```bash
export EMOTIV_CLIENT_ID=<your-client-id>
export EMOTIV_CLIENT_SECRET=<your-client-secret>
python -m eeg_coderbot.cli stream --stream met
```

Example workflow for testing CoderBot control without moving the robot:

```bash
export EMOTIV_CLIENT_ID=<your-client-id>
export EMOTIV_CLIENT_SECRET=<your-client-secret>
export CODERBOT_BASE_URL=http://coderbot.local
export DRY_RUN=true
python -m eeg_coderbot.cli coderbot
```

## Inputs and outputs

### Inputs

- Emotiv Cortex WebSocket messages from `EMOTIV_CORTEX_URL`
- Emotiv application credentials from environment variables
- User-entered or CLI-provided stream type for the stream-printing workflow
- CoderBot API base URL from `CODERBOT_BASE_URL`
- Movement parameters from environment variables

### Outputs

- Terminal output containing login, access, license, subscription, timing, dry-run, and response messages
- Optional CoderBot HTTP requests to move the robot when `DRY_RUN=false`
- No project data files are written by the current workflows

## Running tests

Run all unit tests with:

```bash
python -m unittest discover -s tests
```

The tests avoid live Emotiv and CoderBot services by injecting fake clients where needed.

## Extending the codebase

When adding new behavior, prefer the existing module boundaries:

- Add new environment settings to `eeg_coderbot.config`.
- Add new Cortex API methods to `eeg_coderbot.cortex`.
- Add new CoderBot commands to `eeg_coderbot.coderbot`, preserving dry-run behavior for mutating actions.
- Add testable decision logic to `eeg_coderbot.metrics` or a new focused module.
- Add new mental-state readers under `eeg_coderbot/mental_states/` and register them with `get_algorithm()`.
- Keep orchestration in `eeg_coderbot.workflows` and CLI concerns in `eeg_coderbot.cli`.
- Add unit tests under `tests/` for normal cases, edge cases, and failure cases.

## Known limitations and assumptions

- The code assumes the first headset returned by Cortex is the desired headset.
- The Emotiv Cortex connection and credentials must be configured externally; no interactive credential setup is provided.
- The code reads environment variables but does not automatically parse `.env` files.
- Live Cortex behavior is not covered by the unit tests.
- The legacy CoderBot movement rule is intentionally minimal: it checks whether engagement and excitement are both greater than zero.
- The mental-state algorithms rely on Emotiv-classified Cortex streams and do not perform raw EEG classification.
- The intended CoderBot endpoint, robot model, and lab setup are not documented in the source code.

## To be completed

Future collaborators may want to add:

- More complete command-line options for all configuration values
- Integration tests with mocked Cortex WebSocket messages
- Setup instructions specific to Emotiv account/application registration
- More robust logging configuration
- Sample output or recorded example data

## Citation and authorship

No formal citation, license, or author metadata is included in the repository. If this code is used in a publication or shared project, add the appropriate authors, lab affiliation, and citation details here.
