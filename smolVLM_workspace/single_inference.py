#!/usr/bin/env python3
import argparse
import base64
import json
import time
from io import BytesIO

import requests
from PIL import Image

def image_to_data_url(path: str, quality: int = 80) -> str:
    print(f"[DEBUG] loading image from {path!r}")
    with Image.open(path) as img:
        buf = BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=quality)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"

def run_inference(
    image_path: str,
    instruction: str,
    api_url: str,
    model_name: str = "smolvlm",
    max_tokens: int = 100
):
    try:
        data_url = image_to_data_url(image_path)
    except Exception as e:
        print(f"[ERROR] could not open/encode image: {e}")
        return

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }
        ],
        "max_tokens": max_tokens
    }

    print(f"[DEBUG] sending POST to {api_url}")
    print(f"[DEBUG] payload preview:\n  model = {model_name!r}\n  instruction = {instruction!r}\n  image_url length = {len(data_url)} chars")
    headers = {"Content-Type": "application/json"}

    try:
        t0 = time.time()
        resp = requests.post(api_url, headers=headers, json=payload, timeout=10)
        t1 = time.time()
    except Exception as e:
        print(f"[ERROR] request failed: {e}")
        return

    print(f"[DEBUG] received HTTP {resp.status_code}")
    print(f"[DEBUG] raw response text (first 500 chars):\n{resp.text[:500]!r}")

    try:
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] bad status: {e}")
        return

    t2 = time.time()
    try:
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] failed to parse JSON: {e}")
        return
    t3 = time.time()

    print(f"\nInference + network: {(t1-t0)*1000:.2f} ms")
    print(f"JSON parse:        {(t3-t2)*1000:.2f} ms")
    print("\nModel response:\n")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    p = argparse.ArgumentParser(
        description="Run one SmolVLM inference on a local image file (DEBUG mode)"
    )
    p.add_argument("image", help="Path to an image file (jpeg/png/etc.)")
    p.add_argument(
        "--instruction", "-i",
        default="Describe what you see in the image.",
        help="Text instruction to prefix the image"
    )
    p.add_argument(
        "--api-url", "-u",
        default="http://127.0.0.1:8080/v1/chat/completions",
        help="Your llama.cpp HTTP endpoint"
    )
    p.add_argument(
        "--model", "-m",
        default="smolvlm",
        help="Model name to send in the payload"
    )
    p.add_argument(
        "--max-tokens", "-t",
        type=int,
        default=100,
        help="Maximum tokens to request"
    )
    args = p.parse_args()

    print(f"[DEBUG] args = {args}")
    run_inference(
        args.image,
        args.instruction,
        args.api_url,
        model_name=args.model,
        max_tokens=args.max_tokens
    )

if __name__ == "__main__":
    main()
