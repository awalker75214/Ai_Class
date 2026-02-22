#app/config.py — config + env support


from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    ollama_host: str = "http://localhost:11434"
    model: str = "llama3.2"
    timeout_seconds: int = 60
    max_retries: int = 2
    log_file: str = "nightmare_date.log.jsonl"
    transcript_file: str = "transcript.txt"

    @staticmethod
    def from_env() -> "AppConfig":
        return AppConfig(
            ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            timeout_seconds=int(os.getenv("OLLAMA_TIMEOUT", "60")),
            max_retries=int(os.getenv("OLLAMA_RETRIES", "2")),
            log_file=os.getenv("APP_LOG_FILE", "nightmare_date.log.jsonl"),
            transcript_file=os.getenv("APP_TRANSCRIPT_FILE", "transcript.txt"),
        )
