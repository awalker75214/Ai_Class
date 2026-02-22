# app/cli.py — CLI runner + structured JSONL logging


import argparse
import json
import sys
from datetime import datetime, timezone

from .config import AppConfig
from .ollama_client import OllamaClient, OllamaError
from .nightmare_game import NightmareDateGame


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(log_file: str, event: dict) -> None:
    # JSON Lines: one JSON object per line (easy for later parsing).
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Nightmare Date (Ollama) - Python CLI")
    p.add_argument("--name", help="Player name")
    p.add_argument("--location", help="Date location")
    p.add_argument("--model", help="Override model name (e.g. llama3.2)")
    p.add_argument("--host", help="Override Ollama host (e.g. http://localhost:11434)")
    p.add_argument("--log-file", help="JSONL log file path")
    p.add_argument("--transcript-file", help="Transcript file path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    cfg = AppConfig.from_env()

    host = args.host or cfg.ollama_host
    model = args.model or cfg.model
    log_file = args.log_file or cfg.log_file
    transcript_file = args.transcript_file or cfg.transcript_file

    # Human-friendly start
    print("\n=== Nightmare Date (Python CLI) ===\n")
    name = (args.name or input("Enter your name: ").strip() or "Alex")
    location = (args.location or input("Enter a location: ").strip() or "a quiet coffee shop")

    client = OllamaClient(host=host, timeout_seconds=cfg.timeout_seconds, max_retries=cfg.max_retries)
    game = NightmareDateGame(client=client, model=model)

    try:
        intro = game.start(name=name, location=location)
    except OllamaError as e:
        print(f"\n[ERROR] {e}\n")
        return 1

    print("\n--- SCENE 1 ---\n")
    print(intro.text)
    print()

    log_event(log_file, {
        "ts": utc_now_iso(),
        "event": "scene",
        "scene": 1,
        "player": name,
        "location": location,
        "model": model,
        "host": host,
        "text": intro.text,
    })

    # Save transcript (simple, append)
    with open(transcript_file, "a", encoding="utf-8") as tf:
        tf.write(f"\n=== New Session {utc_now_iso()} ===\n")
        tf.write(f"Player: {name}\nLocation: {location}\n\n")
        tf.write(f"[Scene 1]\n{intro.text}\n\n")

    while True:
        choice = input("Your move (A/B/C or anything; q to quit): ").strip()
        if choice.lower() in ("q", "quit", "exit"):
            print("\n✅ Exiting. You survived… probably.\n")
            log_event(log_file, {"ts": utc_now_iso(), "event": "exit"})
            return 0

        try:
            scene = game.continue_story(player_choice=choice)
        except OllamaError as e:
            print(f"\n[ERROR] {e}\n")
            log_event(log_file, {"ts": utc_now_iso(), "event": "error", "error": str(e)})
            return 1

        print(f"\n--- SCENE {scene.number} ---\n")
        print(scene.text)
        print()

        log_event(log_file, {
            "ts": utc_now_iso(),
            "event": "scene",
            "scene": scene.number,
            "player_input": choice,
            "text": scene.text,
        })

        with open(transcript_file, "a", encoding="utf-8") as tf:
            tf.write(f"[Player]\n{choice}\n\n")
            tf.write(f"[Scene {scene.number}]\n{scene.text}\n\n")


if __name__ == "__main__":
    raise SystemExit(main())
