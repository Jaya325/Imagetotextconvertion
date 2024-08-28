import requests

# Ollama Moondream API endpoint
api_endpoint = "http://localhost:11434/generate"  # Update the endpoint URL if needed

# Define the function to generate content using the Moondream model
def generate_content(prompt):
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Prepare the JSON data payload
    data = {
        "model": "ollama/moondream",
        "prompt": prompt,
    }

    try:
        # Send a POST request to the API endpoint
        response = requests.post(api_endpoint, json=data, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            return result.get('response', 'No response found')
        else:
            # Handle errors
            print(f"Error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
