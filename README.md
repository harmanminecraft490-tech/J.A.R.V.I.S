# J.A.R.V.I.S — Google AI Computer-Use Agent

JARVIS is a Windows desktop AI agent built around a real computer-use loop: **listen → understand → observe → act → verify → recover**.

## First launch

When JARVIS opens for the first time, it asks for the user's **Google AI Studio / Gemini API key**. The credential is stored locally through the Windows credential manager and is never committed to Git.

Google Gemini is the default brain, and Gemini Live is the voice layer. The provider boundary keeps those services replaceable without rewriting the Windows executor.

## Computer use

The current implementation uses Google's Computer Use interface with the **desktop** environment. JARVIS:

1. captures the real Windows desktop;
2. sends the goal + screenshot to the model;
3. receives structured mouse/keyboard desktop actions;
4. converts normalized coordinates to actual screen pixels;
5. executes the action locally;
6. captures the new screen;
7. sends the action result + screenshot back to the same interaction;
8. repeats until completion or a safety/user blocker.

Prompt-injection detection is enabled for screenshot-driven computer use.

## Run

```powershell
python -m pip install -r requirements.txt
python main.py
```

## Configuration

- `JARVIS_MODEL` — Computer Use model, default `gemini-3.8-flash`
- `JARVIS_LIVE_MODEL` — Live voice model, default `gemini-3.8-live`
- `JARVIS_MAX_STEPS` — maximum computer-use loop iterations

## Important distinction

A Google AI Studio key authenticates Google's Gemini services. If your `aq.xxxxxxxxx` credential belongs to a separate AI Hub/proxy that exposes GPT-6 Astra, that endpoint should be added as a separate provider adapter. The computer-use executor is intentionally provider-independent.

## Security

The local executor does not bypass Windows security. High-impact operations should require confirmation, and secrets must never be logged or committed.
