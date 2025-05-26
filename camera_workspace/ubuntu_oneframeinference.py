#!/usr/bin/env python3
import argparse
import base64
import json
import time
import sys
import os

try:
    from picamera2 import Picamera2
except ImportError:
    print("Error: Picamera2 not found. Install with `pip3 install picamera2`.", file=sys.stderr)
    print("Ensure libcamera is installed: `sudo apt install libcamera0 python3-libcamera`", file=sys.stderr)
    sys.exit(1)

try:
    import cv2
except ImportError:
    print("Error: OpenCV not found. Install with `pip3 install opencv-python`.", file=sys.stderr)
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: Requests not found. Install with `pip3 install requests`.", file=sys.stderr)
    sys.exit(1)

def capture_image():
    try:
        # Initialize Picamera2
        picam2 = Picamera2()
        # Configure for still capture at 320x240
        cfg = picam2.create_still_configuration(main={"size": (320, 240)})
        picam2.configure(cfg)
        picam2.start()
        # Allow camera to adjust
        time.sleep(0.5)
        frame = picam2.capture_array()
        picam2.stop()
        return frame
    except Exception as e:
        print(f"Error capturing image: {e}", file=sys.stderr)
        print("Ensure the camera module is enabled and libcamera is configured.", file=sys.stderr)
        sys.exit(1)

def encode_image_to_data_url(frame):
    # Encode as JPEG
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

    # Measure inference (network + server) time
    t0 = time.perf_counter()
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    t1 = time.perf_counter()

    # Measure JSON parsing time
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
    parser = argparse.ArgumentParser(description="Capture one frame and call SmolVLM API on Ubuntu.")
    parser.add_argument("--api", "-u",
                        default="http://127.0.0.1:8080/v1/chat/completions",
                        help="API URL (default: %(default)s)")
    parser.add_argument("--instruction", "-i",
                        default="Describe what you see in the image.",
                        help="Text instruction to send with the image")
    args = parser.parse_args()

    # Check if camera is accessible
    if not os.path.exists("/dev/video0"):
        print("Error: No camera detected at /dev/video0. Ensure camera is connected and enabled.", file=sys.stderr)
        sys.exit(1)

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
