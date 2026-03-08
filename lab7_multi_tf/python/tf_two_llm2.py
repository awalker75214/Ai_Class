import json
import urllib.request
import urllib.error


OLLAMA_URL = "http://localhost:11434/api/generate"

# You can later change these to different models.
BUILDER_MODEL = "llama3.2"
REVIEWER_MODEL = "llama3.2"


def call_ollama(model: str, prompt: str) -> str:
    """Send a prompt to Ollama and return the text response."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            response_body = response.read().decode("utf-8")
            parsed = json.loads(response_body)
            return parsed.get("response", "").strip()
    except urllib.error.URLError as e:
        return f"[ERROR] Could not reach Ollama: {e}"
    except Exception as e:
        return f"[ERROR] Unexpected error: {e}"


def build_builder_prompt() -> str:
    """Prompt for LLM #1: generate Terraform."""
    return """
You are a Terraform Builder.

Generate beginner-friendly Terraform code for AWS that creates:

- 1 VPC with CIDR block 10.0.0.0/16
- 2 public subnets in different availability zones
- 1 internet gateway
- 1 public route table
- route table associations for both public subnets
- Name tags on all resources

Requirements:
- Output only Terraform code
- Use valid Terraform HCL
- Use readable resource names
- Keep the code clear and simple
- Do not include explanations outside the code
""".strip()


def build_reviewer_prompt(terraform_code: str) -> str:
    """Prompt for LLM #2: review Terraform produced by LLM #1."""
    return f"""
You are a senior Terraform reviewer.

Review the Terraform code below.

Check for:
- correctness
- readability
- maintainability
- missing tags
- missing networking pieces
- security concerns
- production-readiness

Be skeptical and specific.

Return your review in exactly this format:

REVIEW_SUMMARY:
<short summary>

STRENGTHS:
- item
- item

ISSUES_FOUND:
- item
- item

RECOMMENDED_FIXES:
- item
- item

IMPROVED_TERRAFORM:
```hcl
<improved terraform here>
