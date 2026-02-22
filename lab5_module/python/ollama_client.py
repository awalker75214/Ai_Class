#app/ollama_client.py — reusable HTTP client + retries


import json
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Any, Dict, Optional


class OllamaError(RuntimeError):
    pass


@dataclass
class GenerateResult:
    response_text: str
    raw: Dict[str, Any]


class OllamaClient:
    def __init__(self, host: str, timeout_seconds: int = 60, max_retries: int = 2):
        self.host = host.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @property
    def generate_url(self) -> str:
        return f"{self.host}/api/generate"

    def generate(
        self,
        model: str,
        prompt: str,
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None,
    ) -> GenerateResult:
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }
        if options:
            payload["options"] = options

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.generate_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 2):  # e.g. retries=2 => attempts 1..3
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                    body = resp.read().decode("utf-8")
                    parsed = json.loads(body)
                    text = (parsed.get("response") or "").strip()
                    return GenerateResult(response_text=text, raw=parsed)

            except urllib.error.HTTPError as e:
                last_error = e
                # HTTP errors are often non-retryable, but we’ll do one retry for 5xx.
                if 500 <= e.code <= 599 and attempt < (self.max_retries + 2):
                    time.sleep(0.5 * attempt)
                    continue
                raise OllamaError(f"HTTP error from Ollama: {e.code} {e.reason}") from e

            except (urllib.error.URLError, TimeoutError) as e:
                last_error = e
                if attempt < (self.max_retries + 2):
                    time.sleep(0.5 * attempt)
                    continue
                raise OllamaError(
                    f"Could not reach Ollama at {self.host}. Is `ollama serve` running?"
                ) from e

            except json.JSONDecodeError as e:
                raise OllamaError("Ollama returned non-JSON output.") from e

            except Exception as e:
                last_error = e
                raise OllamaError(f"Unexpected error calling Ollama: {e}") from e

        raise OllamaError(f"Failed to call Ollama after retries. Last error: {last_error}")
