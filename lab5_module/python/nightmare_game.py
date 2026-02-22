# app/nightmare_game.py — game logic (clean + testable)

from dataclasses import dataclass
from typing import List, Optional
from .ollama_client import OllamaClient


BASE_RULES = (
    "You are a horror-comedy narrator for a 'Nightmare Date' interactive story game. "
    "Keep it PG-13 spooky (no gore). Use classic horror vibes (flickering lights, ominous music cues, "
    "strange townspeople) and include zombies, but keep it non-graphic. "
    "Keep each response under 6 sentences. End with a question and 3 choices labeled A/B/C."
)


@dataclass
class Scene:
    number: int
    text: str
    player_input: Optional[str] = None


class NightmareDateGame:
    def __init__(self, client: OllamaClient, model: str):
        self.client = client
        self.model = model
        self.scenes: List[Scene] = []

    def start(self, name: str, location: str) -> Scene:
        prompt = (
            f"{BASE_RULES}\n\n"
            f"Start the story now. The main character is {name}. "
            f"The date takes place at {location}. Make it creepy, funny, and escalating."
        )
        res = self.client.generate(model=self.model, prompt=prompt, stream=False)
        scene = Scene(number=1, text=res.response_text)
        self.scenes = [scene]
        return scene

    def continue_story(self, player_choice: str) -> Scene:
        transcript = self._transcript_text()
        next_num = len(self.scenes) + 1
        prompt = (
            f"{BASE_RULES}\n\n"
            f"Story so far:\n{transcript}\n\n"
            f"Player chooses: {player_choice}\n"
            f"Continue with SCENE {next_num}."
        )
        res = self.client.generate(model=self.model, prompt=prompt, stream=False)
        scene = Scene(number=next_num, text=res.response_text, player_input=player_choice)
        self.scenes.append(scene)
        return scene

    def _transcript_text(self) -> str:
        lines = []
        for s in self.scenes:
            if s.player_input:
                lines.append(f"[Player] {s.player_input}")
            lines.append(f"[Scene {s.number}] {s.text}")
        return "\n".join(lines).strip()
