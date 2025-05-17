#!/usr/bin/env python3
import argparse
import base64
import json
import time
from io import BytesIO

import requests
from PIL import Image

def image_to_data_url(path: str, quality: int = 80) -> str:
    """
    Load an image from disk, re-encode as JPEG at given quality,
    and return a data URL.
    """
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
    # 1) Prepare payload
    data_url = image_to_data_url(image_path)
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
    headers = {"Content-Type": "application/json"}

    # 2) Send request and time it
    t0 = time.time()
    resp = requests.post(api_url, headers=headers, json=payload)
    t1 = time.time()

    # 3) Parse JSON and time it
    t2 = time.time()
    resp.raise_for_status()
    data = resp.json()
    t3 = time.time()

    # 4) Report
    print(f"Inference + network: {(t1-t0)*1000:.2f} ms")
    print(f"JSON parse:        {(t3-t2)*1000:.2f} ms")
    print("\nModel response:\n")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    p = argparse.ArgumentParser(
        description="Run one SmolVLM inference on a local image file"
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

    run_inference(
        args.image,
        args.instruction,
        args.api_url,
        model_name=args.model,
        max_tokens=args.max_tokens
    )

if __name__ == "__main__":
    main()
