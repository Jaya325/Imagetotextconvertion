#!/usr/bin/env python3
import argparse
import base64
import json
import time
import sys

try:
    from picamera2 import Picamera2
except ImportError:
    print("Error: Picamera2 not found. Install with `sudo apt install python3-picamera2`.", file=sys.stderr)
    sys.exit(1)

import cv2
import requests

def capture_image():
    picam2 = Picamera2()
    # configure for still capture at 640×480
    cfg = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(cfg)
    picam2.start()
    # give camera a moment to adjust
    time.sleep(0.5)
    frame = picam2.capture_array()
    picam2.stop()
    return frame

def encode_image_to_data_url(frame):
    # encode as JPEG
    ret, buf = cv2.imencode('.jpg', frame)
    if not ret:
        raise RuntimeError("Failed to encode frame as JPEG")
    b64 = base64.b64encode(buf.tobytes()).decode('ascii')
    return f"data:image/jpeg;base64,{b64}"

def call_api(api_url, instruction, image_data_url):
    payload = {
        "model": "smolvlm",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }
        ],
        "max_tokens": 100
    }
    headers = {"Content-Type": "application/json"}

    # measure inference (network + server) time
    t0 = time.perf_counter()
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    t1 = time.perf_counter()

    # measure JSON parsing time
    t2 = time.perf_counter()
    data = response.json()
    t3 = time.perf_counter()

    return {
        "status_code": response.status_code,
        "inference_ms": (t1 - t0) * 1000,
        "parse_ms": (t3 - t2) * 1000,
        "data": data
    }

def main():
    parser = argparse.ArgumentParser(description="Capture one frame and call SmolVLM API.")
    parser.add_argument("--api", "-u",
                        default="http://127.0.0.1:8080/v1/chat/completions",
                        help="API URL (default: %(default)s)")
    parser.add_argument("--instruction", "-i",
                        default="Describe what you see in the image.",
                        help="Text instruction to send with the image")
    args = parser.parse_args()

    print("Capturing image from camera…")
    frame = capture_image()

    print("Encoding image…")
    data_url = encode_image_to_data_url(frame)

    print(f"Calling API at {args.api!r} …")
    result = call_api(args.api, args.instruction, data_url)

    print(f"\n== API Response ==")
    print(f"HTTP Status: {result['status_code']}")
    print(f"Inference time: {result['inference_ms']:.2f} ms")
    print(f"JSON parse time: {result['parse_ms']:.2f} ms\n")
    print("Response payload:")
    print(json.dumps(result["data"], indent=2))

if __name__ == "__main__":
    main()
