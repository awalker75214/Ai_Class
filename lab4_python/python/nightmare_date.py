import json
import sys
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"


def ollama_generate(prompt: str) -> str:
    """Call Ollama's /api/generate and return just the 'response' text."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            parsed = json.loads(body)
            return parsed.get("response", "").strip()
    except urllib.error.URLError as e:
        return f"[ERROR] Could not reach Ollama at {OLLAMA_URL}. Is `ollama serve` running?\nDetails: {e}"
    except json.JSONDecodeError:
        return "[ERROR] Ollama returned a non-JSON response."
    except Exception as e:
        return f"[ERROR] Unexpected error: {e}"


def main():
    print("\n=== Nightmare Date (Ollama Python) ===\n")
    name = input("Enter your name: ").strip() or "Alex"
    location = input("Enter a location (e.g., 'Austin coffee shop'): ").strip() or "a quiet coffee shop"

    # System-style rules embedded into the first prompt (simple + classroom-safe).
    base_rules = (
        "You are a horror-comedy narrator for a 'Nightmare Date' interactive story game. "
        "Keep it PG-13 spooky (no gore). Use classic horror vibes (flickering lights, ominous music cues, "
        "strange townspeople) and include zombies, but keep it non-graphic. "
        "Keep each response under 6 sentences. End with a question and 3 choices labeled A/B/C."
    )

    intro_prompt = (
        f"{base_rules}\n\n"
        f"Start the story now. The main character is {name}. The date takes place at {location}. "
        f"Make it creepy, funny, and escalating."
    )

    story = ollama_generate(intro_prompt)
    print("\n--- SCENE 1 ---\n")
    print(story)
    print()

    # Simple “state”: we just keep appending to a running transcript.
    transcript = f"RULES: {base_rules}\nSCENE 1: {story}\n"

    turn = 2
    while True:
        action = input("Your move (type A/B/C or anything; 'q' to quit): ").strip()
        if action.lower() in ("q", "quit", "exit"):
            print("\n✅ Exiting game. Nice survival instincts.\n")
            return

        next_prompt = (
            f"{base_rules}\n\n"
            f"Story so far:\n{transcript}\n"
            f"Player chooses: {action}\n"
            f"Continue with SCENE {turn}."
        )

        story = ollama_generate(next_prompt)
        print(f"\n--- SCENE {turn} ---\n")
        print(story)
        print()

        transcript += f"SCENE {turn}: {story}\n"
        turn += 1


if __name__ == "__main__":
    main()
