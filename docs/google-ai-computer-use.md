# Google AI + Computer Use

JARVIS is now built around Google's current Gemini Computer Use pattern for a real Windows desktop.

## First launch

1. Show a setup dialog requesting the user's Google AI Studio / Gemini API key.
2. Store it locally through the OS credential manager via `keyring`.
3. Do not write the key to Git, `.env`, logs, screenshots, or telemetry.
4. Start the JARVIS session only after a key is available.

## Runtime loop

```text
USER GOAL
   ↓
OBSERVE WINDOWS DESKTOP
   ↓
GEMINI COMPUTER USE
   ↓
STRUCTURED DESKTOP FUNCTION CALL
   ↓
LOCAL VALIDATION / SAFETY
   ↓
MOUSE + KEYBOARD EXECUTOR
   ↓
NEW SCREENSHOT
   ↓
FUNCTION RESULT + SCREENSHOT → GEMINI
   ↺
```

Gemini Computer Use provides normalized 0–999 desktop coordinates; JARVIS converts them to the actual Windows display dimensions before execution. The model chooses the action while the local executor physically performs it.

Prompt-injection detection is enabled for screenshot-based computer use. Safety decisions requiring confirmation are surfaced instead of silently bypassed.

## Voice

The voice subsystem has a Google Gemini Live adapter using the Live API. It is deliberately isolated so the microphone/audio transport can be upgraded independently of the computer-use engine.

## Model configuration

`JARVIS_MODEL` controls the Computer Use model and defaults to `gemini-3.8-flash`.
`JARVIS_LIVE_MODEL` controls the Live voice model and defaults to `gemini-3.8-live`.

The Google AI key authenticates Google's Gemini services. A separate Astra-compatible endpoint can be added behind the provider boundary if the user's API service exposes one; the Windows computer-use executor does not need to change.
