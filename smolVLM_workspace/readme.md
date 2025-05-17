```javascript
# Realtime VLM model

# Start Server llama.cpp
1.chmod +x run_llama.sh
2. ./run_llama.sh



# Python client code for Inference and Benchmarking Live webcam
1. pip install opencv-python requests
2. python smolvlm_inference_client.py --interval 5 --api_url http://127.0.0.1:8080/v1/chat/completions --instruction "Describe what you see in the image."




```
