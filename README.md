# J.A.R.V.I.S — Google AI-powered Windows Computer Agent

JARVIS is a Windows desktop agent designed around a computer-use loop: **listen → understand → observe → act → verify → recover**.

## First launch

The desktop application will ask for the user's Google AI / Gemini API key on first launch. The key is stored locally through the Windows credential store when available and is never committed to Git.

Google AI is the primary brain and voice provider for the initial implementation. The provider is isolated behind adapters so the computer-use runtime can evolve independently.

## Computer use

JARVIS combines:

- screenshot and focused-region observation
- structured computer actions
- deterministic Windows mouse/keyboard execution
- window/process awareness
- filesystem and terminal tools
- action verification and recovery
- task pause/resume/cancel and emergency stop
- concise activity status instead of exposing private chain-of-thought

The model chooses **what** to do; the local executor determines **how** to safely perform the action.

## Security

High-impact actions require confirmation according to the configured policy. Secrets, passwords, API keys, and tokens must not be written to logs or source control.

## Development

The repository is being implemented incrementally. See `docs/architecture.md` for the current design and `docs/roadmap.md` for implementation stages.
