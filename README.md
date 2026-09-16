# J.A.R.V.I.S — Autonomous Windows PC Agent

JARVIS is a Windows desktop agent built around **LISTEN → UNDERSTAND → PLAN → OBSERVE → ACT → VERIFY → RECOVER → COMPLETE**.

## Current build

The launcher is now a premium PySide6 command center with:

- live Windows desktop preview;
- command bar and emergency STOP;
- current-task/progress panel;
- live activity stream;
- brain / vision / executor / safety health cards;
- no first-launch API-key dialog;
- local-first execution through Windows APIs, PowerShell/process control and PyAutoGUI;
- optional local vision reasoning through Ollama (no cloud API key).

## No-key local mode

JARVIS does not require a cloud API key to open. For deterministic commands it can immediately execute useful local actions such as opening applications, creating folders, and taking screenshots.

For visual autonomous tasks, install/run Ollama locally and provide a vision-capable model such as `qwen3-vl:8b`. The default endpoint is `http://127.0.0.1:11434/api/chat` and can be changed with `JARVIS_OLLAMA_URL`. The model can be changed with `JARVIS_LOCAL_MODEL`.

## Run

```powershell
python -m pip install -r requirements.txt
python main.py
```

## Architecture

- `ui/dashboard.py` — premium command-center UI and live desktop preview
- `core/local_agent.py` — no-key local agent loop and Ollama vision adapter
- `computer/executor.py` — deterministic Windows mouse/keyboard/process/filesystem execution
- `vision/screen.py` — screenshot capture/compression
- `brain/google_computer_use.py` — optional Google Computer Use provider
- `voice/` — replaceable voice providers
- `core/` — task/state/risk primitives

The model decides **what** to do; the local executor decides **how** to perform validated actions. Detailed hidden reasoning is not shown in the UI; the activity stream contains concise action/status events.

## Safety

The executor does not bypass Windows security. Emergency STOP releases held mouse/buttons and common modifier keys. High-impact operations should remain behind confirmation/policy controls.

## Optional cloud provider

Google Gemini Computer Use remains available as a provider adapter, but it is no longer required to launch the desktop application. Google documents Computer Use as a screenshot/action loop with client-side execution and prompt-injection detection. See the official Gemini Computer Use documentation before enabling it in an unsandboxed environment.
