#!/usr/bin/env python3
"""
OpenAI Deep Research API caller for FunnelAgent.

Usage:
    python scripts/deep_research.py --prompt-file <path> --output <path>

Environment:
    OPENAI_API_KEY - Your OpenAI API key (or set in .env file)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
except ImportError:
    pass


DEFAULT_MODEL = "o4-mini-deep-research"
MODEL_ALIASES = {
    "o3-deep-research": "o3-deep-research-2025-06-26",
    "o4-mini-deep-research": "o4-mini-deep-research-2025-06-26",
}
TERMINAL_STATUSES = {"completed", "failed", "cancelled", "incomplete"}
DEVELOPER_INSTRUCTIONS = """
You are a professional direct-response market researcher preparing a structured,
data-rich research report for copywriting and funnel strategy.

Do:
- Prioritize real, current, high-signal sources over generic summaries.
- Use web search actively and cite concrete sources for factual claims.
- State uncertainty explicitly when data is unavailable.
- Avoid invented quotes, invented statistics, and invented community discussions.
- Prefer source-grounded bullet lists and structured sections that can feed
  downstream synthesis.
"""


class DeepResearchError(RuntimeError):
    """Raised when the deep research response is unusable."""


def normalize_model_name(model: str) -> str:
    return MODEL_ALIASES.get(model, model)


def build_deep_research_request(model: str, prompt: str) -> dict:
    return {
        "model": normalize_model_name(model),
        "background": True,
        "reasoning": {"summary": "auto"},
        "input": [
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": DEVELOPER_INSTRUCTIONS.strip(),
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    }
                ],
            },
        ],
        "tools": [
            {"type": "web_search_preview"},
            {
                "type": "code_interpreter",
                "container": {"type": "auto", "file_ids": []},
            },
        ],
    }


def wait_for_response(client: OpenAI, response_id: str, poll_interval: int, timeout: int):
    deadline = time.time() + timeout
    while True:
        response = client.responses.retrieve(response_id)
        status = getattr(response, "status", None)
        if status in TERMINAL_STATUSES or status is None:
            return response
        if time.time() >= deadline:
            raise DeepResearchError(
                f"Timed out waiting for deep research response {response_id} (last status: {status})"
            )
        time.sleep(poll_interval)


def extract_report_text(response) -> str:
    output_text = getattr(response, "output_text", "")
    if output_text:
        return output_text

    for item in reversed(getattr(response, "output", [])):
        if getattr(item, "type", None) != "message":
            continue
        for content_block in getattr(item, "content", []):
            text = getattr(content_block, "text", "")
            if text:
                return text
    return ""


def extract_citations(response) -> list[dict]:
    citations = []
    for item in reversed(getattr(response, "output", [])):
        if getattr(item, "type", None) != "message":
            continue
        for content_block in getattr(item, "content", []):
            annotations = getattr(content_block, "annotations", None) or []
            for annotation in annotations:
                url = getattr(annotation, "url", None)
                title = getattr(annotation, "title", None)
                if not url or not title:
                    continue
                citations.append(
                    {
                        "title": title,
                        "url": url,
                        "start_index": getattr(annotation, "start_index", None),
                        "end_index": getattr(annotation, "end_index", None),
                    }
                )
        if citations:
            break
    return citations


def validate_report(report_text: str, citations: list[dict]) -> None:
    stripped = report_text.strip()
    if not stripped:
        raise DeepResearchError("Deep research returned no report text.")

    lowered = stripped.lower()
    refusal_markers = [
        "i'm sorry",
        "i cannot provide that",
        "i can’t provide that",
        "i can't provide that",
    ]
    if any(marker in lowered for marker in refusal_markers):
        raise DeepResearchError("Deep research returned a refusal instead of a report.")

    if not citations:
        raise DeepResearchError("Deep research returned no citations.")


def dedupe_citations(citations: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for citation in citations:
        key = (citation["title"], citation["url"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(citation)
    return unique


def render_report(report_text: str, citations: list[dict], response_id: str, model: str) -> str:
    lines = [report_text.strip(), "", "## Sources"]
    for citation in dedupe_citations(citations):
        lines.append(f"- [{citation['title']}]({citation['url']})")
    lines.extend(
        [
            "",
            "## Metadata",
            f"- Response ID: `{response_id}`",
            f"- Model: `{model}`",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def write_metadata(output_path: Path, response, citations: list[dict]) -> None:
    metadata_path = output_path.with_suffix(output_path.suffix + ".meta.json")
    payload = {
        "response_id": getattr(response, "id", None),
        "status": getattr(response, "status", None),
        "model": getattr(response, "model", None),
        "citations": citations,
        "usage": getattr(response, "usage", None).model_dump()
        if hasattr(getattr(response, "usage", None), "model_dump")
        else None,
    }
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Run OpenAI Deep Research")
    parser.add_argument("--prompt-file", required=True, help="Path to file containing the research prompt")
    parser.add_argument("--output", required=True, help="Path to write the research output")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="OpenAI deep research model to use (default: o4-mini-deep-research)",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        help="Polling interval in seconds while waiting for background completion",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Maximum wait time in seconds for the background response",
    )
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set. Create a .env file or export the variable.", file=sys.stderr)
        sys.exit(1)

    prompt_path = Path(args.prompt_file)
    if not prompt_path.exists():
        print(f"Error: Prompt file not found: {prompt_path}", file=sys.stderr)
        sys.exit(1)

    prompt = prompt_path.read_text(encoding="utf-8")
    print(f"Prompt loaded ({len(prompt)} chars)", file=sys.stderr)

    # Initialize client with extended timeout for deep research models (up to 30 min)
    client = OpenAI(api_key=api_key, timeout=1800.0)
    request = build_deep_research_request(model=args.model, prompt=prompt)
    print(
        f"Starting deep research with {request['model']} in background mode...",
        file=sys.stderr,
    )

    try:
        initial_response = client.responses.create(**request)
        response_id = getattr(initial_response, "id", None)
        if not response_id:
            raise DeepResearchError("Deep research response did not include a response id.")

        final_response = wait_for_response(
            client=client,
            response_id=response_id,
            poll_interval=args.poll_interval,
            timeout=args.timeout,
        )
        if getattr(final_response, "status", None) != "completed":
            error = getattr(final_response, "error", None)
            if error is not None:
                raise DeepResearchError(str(error))
            raise DeepResearchError(
                f"Deep research finished with status {getattr(final_response, 'status', None)}"
            )

        report_text = extract_report_text(final_response)
        citations = extract_citations(final_response)
        validate_report(report_text, citations)

    except DeepResearchError as exc:
        print(f"Deep research error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"API Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_report(
            report_text=report_text,
            citations=citations,
            response_id=final_response.id,
            model=request["model"],
        ),
        encoding="utf-8",
    )
    write_metadata(output_path, final_response, citations)

    word_count = len(report_text.split())
    print(
        f"Research complete! {word_count} words written to {output_path} with {len(citations)} citations",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
