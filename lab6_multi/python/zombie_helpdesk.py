import json
import urllib.request
import urllib.error


OLLAMA_URL = "http://localhost:11434/api/generate"

# You can use the same model for both roles at first.
# Later, students can try different models for story vs game master.
STORY_MODEL = "llama3.2"
GM_MODEL = "llama3.2"


def call_ollama(model: str, prompt: str) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            body = response.read().decode("utf-8")
            parsed = json.loads(body)
            return parsed.get("response", "").strip()
    except urllib.error.URLError as e:
        return f"[ERROR] Could not reach Ollama: {e}"
    except Exception as e:
        return f"[ERROR] Unexpected error: {e}"


def build_story_prompt(player_name: str, office_location: str, issue: str, history: str, last_action: str) -> str:
    return f"""
You are the Story Generator for a horror-comedy game called "Zombie Help Desk."

Your job:
- Write a short, funny, spooky office incident scene
- Keep it PG-13
- No gore
- Include zombies, creepy office behavior, and absurd corporate details
- Keep the response to 5 sentences or fewer
- Focus on atmosphere, escalation, and humor

Context:
- Player name: {player_name}
- Office location: {office_location}
- Original issue: {issue}
- Previous history: {history if history else "None yet"}
- Player's latest action: {last_action if last_action else "Start the story"}

Write only the scene narrative.
""".strip()


def build_gm_prompt(scene_text: str, history: str) -> str:
    return f"""
You are the Game Master for a horror-comedy office survival game called "Zombie Help Desk."

Your job:
- Read the latest story scene
- Determine the current game state
- Keep it fun, coherent, and structured
- No gore
- Office-horror tone with zombie elements

Return ONLY valid JSON in this exact structure:

{{
  "threat_level": 1,
  "office_safe": false,
  "escalate_to_security": false,
  "escalate_to_facilities": false,
  "escalate_to_incident_response": false,
  "zombie_risk": "low",
  "gm_comment": "short explanation",
  "next_choices": [
    "choice 1",
    "choice 2",
    "choice 3"
  ]
}}

Rules:
- threat_level must be an integer from 1 to 5
- zombie_risk must be one of: "low", "moderate", "high", "critical"
- next_choices must contain exactly 3 strings
- office_safe must be true or false
- The escalations must be true or false
- The gm_comment should be short and useful

Story history:
{history if history else "None yet"}

Latest scene:
{scene_text}
""".strip()


def parse_gm_json(gm_text: str) -> dict:
    try:
        start = gm_text.find("{")
        end = gm_text.rfind("}")
        if start != -1 and end != -1:
            gm_text = gm_text[start:end+1]
        return json.loads(gm_text)
    except Exception:
        return {
            "threat_level": 3,
            "office_safe": False,
            "escalate_to_security": True,
            "escalate_to_facilities": True,
            "escalate_to_incident_response": False,
            "zombie_risk": "moderate",
            "gm_comment": "The Game Master became confused, which is not a great sign in a zombie office.",
            "next_choices": [
                "Lock the server room",
                "Call Facilities",
                "Hide under the help desk"
            ]
        }


def print_status(gm_state: dict):
    print("\n=== GAME MASTER STATUS ===")
    print(f"Threat Level: {gm_state.get('threat_level')}/5")
    print(f"Office Safe: {gm_state.get('office_safe')}")
    print(f"Zombie Risk: {gm_state.get('zombie_risk')}")
    print(f"Escalate to Security: {gm_state.get('escalate_to_security')}")
    print(f"Escalate to Facilities: {gm_state.get('escalate_to_facilities')}")
    print(f"Escalate to Incident Response: {gm_state.get('escalate_to_incident_response')}")
    print(f"GM Comment: {gm_state.get('gm_comment')}")

    print("\nNext Choices:")
    choices = gm_state.get("next_choices", [])
    for i, choice in enumerate(choices, start=1):
        print(f"  {i}. {choice}")


def main():
    print("\n🧟 Welcome to Zombie Help Desk\n")

    player_name = input("Enter your name: ").strip() or "Theo"
    office_location = input("Enter office location: ").strip() or "Austin Office"
    issue = input("Enter the initial support issue: ").strip() or "Users hear groaning from the server room."

    history_entries = []
    last_action = ""

    for turn in range(1, 6):
        print(f"\n{'=' * 20} TURN {turn} {'=' * 20}")

        history_text = "\n".join(history_entries)

        story_prompt = build_story_prompt(
            player_name=player_name,
            office_location=office_location,
            issue=issue,
            history=history_text,
            last_action=last_action
        )
        story_scene = call_ollama(STORY_MODEL, story_prompt)

        print("\n--- STORY GENERATOR ---")
        print(story_scene)

        gm_prompt = build_gm_prompt(scene_text=story_scene, history=history_text)
        gm_raw = call_ollama(GM_MODEL, gm_prompt)
        gm_state = parse_gm_json(gm_raw)

        print_status(gm_state)

        history_entries.append(f"TURN {turn} STORY: {story_scene}")
        history_entries.append(f"TURN {turn} GM: {json.dumps(gm_state)}")

        if gm_state.get("threat_level", 1) >= 5 or gm_state.get("zombie_risk") == "critical":
            print("\n☠️ The office situation has become critically cursed. Simulation ending.")
            break

        choices = gm_state.get("next_choices", [])
        if len(choices) < 3:
            choices = [
                "Lock the server room",
                "Call Security",
                "Investigate the coffee machine"
            ]

        print("\nChoose your action:")
        print(f"1. {choices[0]}")
        print(f"2. {choices[1]}")
        print(f"3. {choices[2]}")
        print("Q. Quit")

        user_choice = input("\nYour choice: ").strip().lower()

        if user_choice == "q":
            print("\n✅ Exiting Zombie Help Desk. HR will be informed if possible.")
            break
        elif user_choice == "1":
            last_action = choices[0]
        elif user_choice == "2":
            last_action = choices[1]
        elif user_choice == "3":
            last_action = choices[2]
        else:
            last_action = user_choice

    print("\n🎉 Game over. The help desk has seen things no ticketing system should ever see.\n")


if __name__ == "__main__":
    main()
