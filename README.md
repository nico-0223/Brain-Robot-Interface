# EEG CoderBot Emotiv Integration

## Overview

This repository contains Python code for connecting to Emotiv Cortex, reading Emotiv-classified EEG-related streams, and optionally sending movement commands to a CoderBot HTTP API.

The current codebase is organized as a small package named `eeg_coderbot`. The top-level scripts are compatibility wrappers that call the package CLI.

## What this project currently does

The repository currently supports these workflows:

1. **Print an Emotiv stream**: subscribe to a selected Cortex stream and print incoming messages.
2. **Move CoderBot from performance metrics**: subscribe to the Emotiv `met` stream and call CoderBot movement when engagement and excitement are both positive.
3. **Run mental-state algorithms**: subscribe to Emotiv-classified `met` or `com` streams and map selected mental states or mental commands to different CoderBot movement settings.

The code does **not** implement raw EEG classification. Mental-state decisions are based on values already classified by Emotiv Cortex streams.

## Actual repository contents

```text
.
├── .env.example
├── README.md
├── eeg_coderbot/
│   ├── __init__.py
│   ├── cli.py
│   ├── coderbot.py
│   ├── config.py
│   ├── cortex.py
│   ├── metrics.py
│   ├── workflows.py
│   └── mental_states/
│       ├── __init__.py
│       └── algorithms.py
├── emotiv_coderbot_AsusLab.py
├── emotiv_dataStream_asusLab.py
├── emotiv_mental_states_AsusLab.py
├── requirements.txt
└── tests/
    ├── test_coderbot.py
    ├── test_config.py
    ├── test_mental_states.py
    └── test_metrics.py
```

## File and folder guide

### Top-level files

- `.env.example`: example environment variables for Emotiv Cortex, CoderBot, dry-run mode, and movement settings.
- `README.md`: this documentation file.
- `requirements.txt`: runtime Python dependencies.
- `emotiv_dataStream_asusLab.py`: compatibility wrapper for the stream-printing workflow.
- `emotiv_coderbot_AsusLab.py`: compatibility wrapper for the original performance-metrics-to-CoderBot workflow.
- `emotiv_mental_states_AsusLab.py`: compatibility wrapper for the mental-state algorithm workflow.

### Package files

- `eeg_coderbot/__init__.py`: package exports for the main configuration classes.
- `eeg_coderbot/cli.py`: command-line parser and workflow routing.
- `eeg_coderbot/config.py`: centralized configuration dataclasses loaded from environment variables.
- `eeg_coderbot/cortex.py`: Emotiv Cortex JSON-RPC WebSocket client wrapper.
- `eeg_coderbot/coderbot.py`: CoderBot HTTP client with dry-run support.
- `eeg_coderbot/metrics.py`: helper functions for mapping metric values and preserving the original movement condition.
- `eeg_coderbot/workflows.py`: orchestration code for Cortex sessions, stream subscriptions, and CoderBot actions.
- `eeg_coderbot/mental_states/__init__.py`: exports the mental-state algorithm classes and registry helpers.
- `eeg_coderbot/mental_states/algorithms.py`: mental-state reading algorithms based on Emotiv `met` and `com` streams.

### Tests

- `tests/test_config.py`: tests environment configuration parsing.
- `tests/test_coderbot.py`: tests CoderBot API behavior and dry-run behavior.
- `tests/test_metrics.py`: tests metric helper functions.
- `tests/test_mental_states.py`: tests mental-state algorithms and algorithm registry behavior.

## Installation

### 1. Create a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Runtime dependencies currently listed in `requirements.txt`:

- `requests`
- `websockets`

The tests use Python's standard-library `unittest` module.

## Configuration

The code reads configuration from environment variables. It does not automatically load `.env` files. Use `.env.example` as a template and load variables with your shell or environment manager.

```bash
cp .env.example .env
```

Environment variables currently used:

| Variable | Default | Used for |
| --- | --- | --- |
| `EMOTIV_CORTEX_URL` | `wss://localhost:6868` | Emotiv Cortex WebSocket URL. |
| `EMOTIV_CLIENT_ID` | empty | Emotiv application client ID. |
| `EMOTIV_CLIENT_SECRET` | empty | Emotiv application client secret. |
| `CODERBOT_BASE_URL` | empty | CoderBot HTTP API base URL. Required unless `DRY_RUN=true`. |
| `DRY_RUN` | `false` | Prints CoderBot actions without sending mutating HTTP requests. |
| `CODERBOT_MOVE_SPEED` | `100` | Default movement speed for the legacy metrics workflow. |
| `CODERBOT_MOVE_ELAPSE` | `1` | Default movement duration for the legacy metrics workflow. |
| `EXPERIMENT_SECONDS` | `120` | Runtime duration for metrics and mental-state workflows. |

Do not commit real Emotiv credentials or production CoderBot URLs.

## Required external services for live runs

Live workflows require:

- Emotiv Launcher/Cortex running and reachable at `EMOTIV_CORTEX_URL`.
- A connected Emotiv headset visible to Cortex.
- Valid Emotiv application credentials.
- A reachable CoderBot HTTP API if `DRY_RUN=false` and a workflow sends CoderBot movements.

Unit tests do not require live Emotiv or CoderBot services.

## Dry-run mode

Set `DRY_RUN=true` to prevent mutating CoderBot HTTP requests. In dry-run mode, CoderBot actions are printed instead of posted.

Example:

```bash
export DRY_RUN=true
python emotiv_mental_states_AsusLab.py
```

Example dry-run output from the CoderBot client:

```text
DRY RUN: would POST http://coderbot.local/control/move with {'speed': 100, 'elapse': 1}
```

Dry-run mode affects CoderBot actions only. The workflows still connect to Emotiv Cortex and read stream data.

## How to run

### Print an Emotiv stream

Using the compatibility wrapper:

```bash
python emotiv_dataStream_asusLab.py
```

Using the package CLI:

```bash
python -m eeg_coderbot.cli stream --stream met --message-count 100
```

Supported stream names are defined in `eeg_coderbot.workflows` and currently include:

```text
eeg, met, mot, dev, eq, pow, com, fac, sys
```

### Run the legacy metrics-to-CoderBot workflow

Using the compatibility wrapper:

```bash
python emotiv_coderbot_AsusLab.py
```

Using the package CLI:

```bash
python -m eeg_coderbot.cli coderbot
```

This workflow subscribes to the Emotiv `met` stream. It sends a CoderBot move request when engagement and excitement are both greater than zero.

### Run a mental-state algorithm

Using the compatibility wrapper:

```bash
python emotiv_mental_states_AsusLab.py
```

Using the package CLI:

```bash
python -m eeg_coderbot.cli mental-states --algorithm performance-threshold
python -m eeg_coderbot.cli mental-states --algorithm mental-command
```

## Mental-state algorithms currently included

Mental-state algorithms are in `eeg_coderbot/mental_states/algorithms.py`.

| Algorithm | Emotiv stream | Behavior |
| --- | --- | --- |
| `performance-threshold` | `met` | Reads Emotiv performance metric positions used by the original script. It can classify `focused`, `relaxed`, `stressed`, `engaged_excited`, `interested`, `neutral`, or `no_signal`. Some states map to different CoderBot movement speeds/durations. |
| `mental-command` | `com` | Reads Emotiv mental-command action and power values. Known actions such as `push`, `pull`, `lift`, `drop`, `left`, and `right` map to different CoderBot movement speeds/durations when power is above threshold. |

The movement mappings use the existing CoderBot `move` request only. This repository does not currently document separate CoderBot endpoints for turning, stopping, or other robot-specific actions.

## Inputs and outputs

### Inputs

- Emotiv Cortex JSON-RPC responses and subscription messages from `EMOTIV_CORTEX_URL`.
- Emotiv credentials from environment variables.
- A selected stream name or mental-state algorithm name.
- Optional CoderBot base URL and movement settings from environment variables.

### Outputs

- Terminal logs showing login/access/session/subscription messages and interpreted mental states.
- Optional CoderBot HTTP POST requests to `{CODERBOT_BASE_URL}/control/move` when dry-run mode is disabled.
- No repository data files are written by the current workflows.

## Running tests

Run all tests:

```bash
python -m unittest discover -s tests
```

The current tests cover configuration parsing, CoderBot dry-run and HTTP behavior, metric helpers, mental-state algorithms, and algorithm registry errors.

## Known limitations and assumptions

- The code assumes the first headset returned by Cortex is the intended headset.
- `.env` files are not loaded automatically.
- The unit tests do not exercise a live Emotiv Cortex WebSocket connection.
- The mental-state algorithms use Emotiv-classified streams and do not classify raw EEG.
- CoderBot movement support is limited to the existing `move` call used by this repository.
- The repository does not include sample data, notebooks, packaging metadata, CI configuration, or a formal license file.

## Suggested future improvements

- Add command-line flags for more configuration values.
- Add integration tests with mocked Cortex WebSocket traffic.
- Document the exact Emotiv headset, Cortex version, and CoderBot API expected by the lab setup.
- Add sample stream messages for development without hardware.
- Add project packaging metadata if this should be installed as a package.

## Citation and authorship

No formal citation, license, or author metadata is currently included in the repository. Add project authors, lab affiliation, and citation details here if this code is used in a publication or shared externally.
