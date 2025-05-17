import cv2
import time
import base64
import json
import argparse
import requests


def parse_args():
    parser = argparse.ArgumentParser(description="SmolVLM Webcam Demo with Inference Timing")
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Interval between requests in seconds (default: 5.0)",
    )
    parser.add_argument(
        "--api_url",
        type=str,
        default="http://127.0.0.1:8080/v1/chat/completions",
        help="Base API URL",
    )
    parser.add_argument(
        "--instruction",
        type=str,
        default="Describe what you see in the image.",
        help="Instruction for the model",
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=100,
        help="Maximum tokens to request (default: 100)",
    )
    return parser.parse_args()


def capture_frame(camera, width=640, height=480):
    """
    Capture a single frame from the webcam and resize it.
    Returns the BGR image or None if failed.
    """
    ret, frame = camera.read()
    if not ret:
        return None
    return cv2.resize(frame, (width, height))


def encode_image_to_data_url(frame, quality=80):
    """
    Encode an OpenCV BGR image to a JPEG data URL (base64).
    """
    ret, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ret:
        raise ValueError("Failed to encode frame to JPEG")
    jpg_bytes = buf.tobytes()
    b64 = base64.b64encode(jpg_bytes).decode('utf-8')
    return f"data:image/jpeg;base64,{b64}"


def send_request(api_url, instruction, data_url, max_tokens=100, model="smolvlm"):
    """
    Send a POST request to the API with the given instruction and image data URL.
    Returns the API response JSON.
    """
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        "max_tokens": max_tokens,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()


def main():
    args = parse_args()

    # Initialize webcam
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Camera opened. Starting inference loop...")
    inference_times = []
    request_count = 0
    last_start_time = None
    image_id = 0

    try:
        while True:
            image_id += 1
            # Capture frame
            frame = capture_frame(camera)
            if frame is None:
                print(f"Warning: Failed to capture frame for Image ID {image_id}")
                continue

            # Encode to Data URL
            data_url = encode_image_to_data_url(frame)

            # Record start time
            start_time = time.time() * 1000  # ms

            # Send request
            try:
                result = send_request(
                    args.api_url,
                    args.instruction,
                    data_url,
                    max_tokens=args.max_tokens,
                )
            except Exception as e:
                print(f"Error on request for Image ID {image_id}: {e}")
                continue

            # Record end time
            end_time = time.time() * 1000  # ms
            inference_time = end_time - start_time
            inference_times.append(inference_time)
            request_count += 1

            # Time since last inference
            since_last = (
                start_time - last_start_time
            ) if last_start_time is not None else None
            last_start_time = start_time

            # Display results
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            avg_time = sum(inference_times) / len(inference_times)
            print("""
========================================
Image ID          : {id}
Inference Time    : {inf:.2f} ms
Since Last        : {since_last}
Average Time      : {avg:.2f} ms over {count} requests
Model Response    : {resp}
========================================
""".format(
                id=image_id,
                inf=inference_time,
                since_last=f"{since_last:.2f} ms" if since_last is not None else "N/A",
                avg=avg_time,
                count=request_count,
                resp=content.strip().replace("\n", " "),
            ))

            # Wait for next interval
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("Stopping inference loop.")
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
