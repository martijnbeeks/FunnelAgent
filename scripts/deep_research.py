#!/usr/bin/env python3
"""
ChatGPT Deep Research API caller for FunnelAgent.

Usage:
    python scripts/deep_research.py --prompt-file <path> --output <path>

Environment:
    OPENAI_API_KEY - Your OpenAI API key (or set in .env file)
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv
    # Load .env from project root
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
except ImportError:
    pass  # dotenv is optional if env var is set directly


def main():
    parser = argparse.ArgumentParser(description="Run ChatGPT Deep Research")
    parser.add_argument("--prompt-file", required=True, help="Path to file containing the research prompt")
    parser.add_argument("--output", required=True, help="Path to write the research output")
    parser.add_argument("--model", default="o4-mini-deep-research", help="OpenAI model to use (default: o4-mini-deep-research)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set. Create a .env file or export the variable.", file=sys.stderr)
        sys.exit(1)

    # Read prompt
    prompt_path = Path(args.prompt_file)
    if not prompt_path.exists():
        print(f"Error: Prompt file not found: {prompt_path}", file=sys.stderr)
        sys.exit(1)

    prompt = prompt_path.read_text(encoding="utf-8")
    print(f"Prompt loaded ({len(prompt)} chars)", file=sys.stderr)

    # Initialize client with extended timeout for deep research models (up to 30 min)
    client = OpenAI(api_key=api_key, timeout=1800.0)

    print("Starting deep research (this may take several minutes)...", file=sys.stderr)

    try:
        response = client.responses.create(
            model=args.model,
            input=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            tools=[
                {
                    "type": "web_search_preview"
                }
            ],
        )

        # Extract text content from response
        output_text = ""
        for item in response.output:
            if item.type == "message":
                for content_block in item.content:
                    if content_block.type == "output_text":
                        output_text += content_block.text

        if not output_text:
            print("Warning: No text content in response", file=sys.stderr)
            # Fallback: try to get any text from the response
            output_text = str(response.output)

    except Exception as e:
        error_msg = str(e)
        # If o3 fails, suggest alternatives
        if "model" in error_msg.lower() or "not found" in error_msg.lower():
            print(f"Model '{args.model}' not available. Trying o4-mini-deep-research...", file=sys.stderr)
            try:
                response = client.responses.create(
                    model="o4-mini-deep-research",
                    input=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    tools=[
                        {
                            "type": "web_search_preview"
                        }
                    ],
                )
                output_text = ""
                for item in response.output:
                    if item.type == "message":
                        for content_block in item.content:
                            if content_block.type == "output_text":
                                output_text += content_block.text
            except Exception as e2:
                print(f"Error with fallback model: {e2}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"API Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")

    word_count = len(output_text.split())
    print(f"Research complete! {word_count} words written to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
