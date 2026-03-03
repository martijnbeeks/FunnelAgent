#!/usr/bin/env python3
"""
Gemini API image generator for FunnelAgent.

Usage:
    # Text-to-image (Imagen)
    python scripts/generate_image.py --prompt-file <path> --output <path> [--aspect-ratio 1:1]

    # Image generation with product reference image (Gemini Flash)
    python scripts/generate_image.py --prompt-file <path> --output <path> --reference-image <path> [--aspect-ratio 1:1]

When --reference-image is provided, the script uses Gemini's multimodal
generate_content API to pass the reference image alongside the text prompt.
This is used for sections that need the product bottle composited into the scene.

Environment:
    GEMINI_API_KEY - Your Gemini API key (or set in .env file)
"""

import argparse
import io
import os
import sys
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not installed. Run: pip install google-genai", file=sys.stderr)
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
except ImportError:
    pass


def generate_with_imagen(client, prompt, aspect_ratio, model):
    """Text-to-image generation using Imagen API."""
    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config={
            "number_of_images": 1,
            "aspect_ratio": aspect_ratio,
            "image_size": "1K",
        },
    )

    if not response.generated_images:
        print("Error: No images returned by the API", file=sys.stderr)
        sys.exit(1)

    return response.generated_images[0].image.image_bytes


def generate_with_reference(client, prompt, reference_path, aspect_ratio):
    """Image generation with a reference image using Gemini's multimodal API."""
    if Image is None:
        print("Error: Pillow package not installed. Run: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    ref_image = Image.open(reference_path)
    print(f"Reference image loaded: {reference_path} ({ref_image.size[0]}x{ref_image.size[1]})", file=sys.stderr)

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, ref_image],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                image_size="1K",
            ),
        ),
    )

    if not response.candidates or not response.candidates[0].content.parts:
        print("Error: No image returned by the API", file=sys.stderr)
        sys.exit(1)

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data

    print("Error: Response contained no image data", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate images via Gemini API")
    parser.add_argument("--prompt-file", required=True, help="Path to file containing the image prompt")
    parser.add_argument("--output", required=True, help="Path to save the generated image (PNG)")
    parser.add_argument("--aspect-ratio", default="1:1", help="Aspect ratio (default: 1:1)")
    parser.add_argument("--model", default="imagen-4.0-generate-001", help="Imagen model (used when no reference image)")
    parser.add_argument("--reference-image", help="Path to a reference image (e.g., product photo) to include in the generation request")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set. Create a .env file or export the variable.", file=sys.stderr)
        sys.exit(1)

    prompt_path = Path(args.prompt_file)
    if not prompt_path.exists():
        print(f"Error: Prompt file not found: {prompt_path}", file=sys.stderr)
        sys.exit(1)

    prompt = prompt_path.read_text(encoding="utf-8").strip()
    print(f"Prompt loaded ({len(prompt)} chars)", file=sys.stderr)

    if args.reference_image:
        ref_path = Path(args.reference_image)
        if not ref_path.exists():
            print(f"Error: Reference image not found: {ref_path}", file=sys.stderr)
            sys.exit(1)

    client = genai.Client(api_key=api_key)

    print("Generating image (this may take a moment)...", file=sys.stderr)

    try:
        if args.reference_image:
            print("Using multimodal generation with reference image", file=sys.stderr)
            image_bytes = generate_with_reference(client, prompt, Path(args.reference_image), args.aspect_ratio)
        else:
            image_bytes = generate_with_imagen(client, prompt, args.aspect_ratio, args.model)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(image_bytes)

        print(f"Image saved to {output_path}", file=sys.stderr)

    except Exception as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
