import json
import urllib.request
import urllib.error


OLLAMA_URL = "http://localhost:11434/api/generate"

BUILDER_MODEL = "llama3.2"
REVIEWER_MODEL = "llama3.2"


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
        with urllib.request.urlopen(req, timeout=120) as response:
            body = response.read().decode("utf-8")
            parsed = json.loads(body)
            return parsed.get("response", "").strip()
    except urllib.error.URLError as e:
        return f"[ERROR] Could not reach Ollama: {e}"
    except Exception as e:
        return f"[ERROR] Unexpected error: {e}"


def build_builder_prompt() -> str:
    return """
You are a Terraform Builder.

Your task:
Generate Terraform code for AWS that creates:

- 1 VPC with CIDR block 10.0.0.0/16
- 2 public subnets in different availability zones
- 1 internet gateway
- 1 public route table
- route table associations for both public subnets
- consistent Name tags on all resources

Requirements:
- Output Terraform code only
- Use AWS provider
- Use clear resource names
- Use valid Terraform HCL
- Keep the solution beginner-friendly and readable
- Include variables only if truly needed
- Do not include explanations outside the code
""".strip()


def build_reviewer_prompt(terraform_code: str) -> str:
    return f"""
You are a strict Terraform Reviewer.

Review the Terraform code below.

Your job:
- Identify strengths
- Identify problems
- Identify missing resources or best practices
- Identify security or maintainability concerns
- Suggest improvements
- If possible, provide an improved version

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
