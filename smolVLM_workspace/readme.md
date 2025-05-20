```javascript
# Realtime VLM model

# Steps to install the server
   -- command to run in terminal
      ``` git clone https://github.com/ggerganov/llama.cpp.git ```

# Start Server llama.cpp
1.chmod +x run_500m_server.sh
2. ./run_500m_server.sh


# Client App 1
# Python client code for Inference and Benchmarking Live webcam
1. pip install opencv-python requests
2. python smolvlm_inference_client.py --interval 5 --api_url http://127.0.0.1:8080/v1/chat/completions --instruction "Describe what you see in the image."

# Client App 2
# open html page in browser


# RPI Device- Single Inference

1. pip install requests pillow
2. python single_inference.py path/to/your.jpg \
  --instruction "What’s in this picture?" \
  --api-url http://127.0.0.1:8080/v1/chat/completions


```


# for the installation of camera system librery libcamera in RPI
```
sudo apt update
sudo apt install libcap-dev
pip install picamera2 --break-system-packages
```
- If the above commands does not work try the below method to install it
  ```
sudo apt update
sudo apt install libevent-dev
meson setup --reconfigure -Dcam=enabled build
cd build
ninja
sudo ninja install
```
- The above commands build succesfully check the below command for cam version
```
 cam --version
 ```
  - If this works, you can proceed to use cam (e.g., cam --list to list cameras).






  
