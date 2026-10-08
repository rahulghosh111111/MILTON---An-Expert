#!/usr/bin/env python3
"""Entry point for MILTON.

Each turn: capture input (typed or spoken) -> capture screen_context ->
ask the brain (Claude, per milton/prompts/system_prompt.txt) -> speak the
reply -> run any un-gated actions -> persist the memory_update -> repeat.
"""

import argparse
import sys

from milton import asr, brain, config, executor, memory as memory_mod
from milton import screen_context as screen_mod
from milton import tts


def run_turn(transcript, mem):
    screen = screen_mod.get_screen_context()
    response = brain.get_response(transcript, screen, mem.as_dict())

    reply = response.get("spoken_reply", "")
    if reply:
        print(f"MILTON: {reply}")
        tts.speak(reply)

    actions = response.get("actions") or []
    if actions:
        executor.execute_actions(actions, screen)

    mem.apply_update(response.get("memory_update"), brain.now_iso())

    clarification = response.get("clarification_needed")
    if clarification:
        print(f"[clarification] {clarification}")

    return response


def main():
    parser = argparse.ArgumentParser(description="MILTON assistant loop")
    parser.add_argument("--mode", choices=["text", "voice"], default=config.INPUT_MODE)
    args = parser.parse_args()

    if not config.ANTHROPIC_API_KEY:
        print("Set ANTHROPIC_API_KEY in your .env file before running.", file=sys.stderr)
        sys.exit(1)

    mem = memory_mod.Memory()
    print(f"MILTON is listening ({args.mode} mode). Ctrl+C to quit.")

    while True:
        try:
            if args.mode == "voice":
                transcript = asr.listen_from_mic()
                if not transcript:
                    continue
                print(f"You said: {transcript}")
            else:
                transcript = asr.listen_from_console()
                if not transcript.strip():
                    continue

            run_turn(transcript, mem)

        except KeyboardInterrupt:
            print("\nShutting down.")
            break
        except Exception as exc:
            print(f"[error] {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
