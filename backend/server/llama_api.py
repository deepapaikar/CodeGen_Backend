from flask import Flask, request, jsonify
from llama_cpp import Llama  # Import the LLaMA Python wrapper

app = Flask(__name__)

# Load the LLaMA model
print("Loading model...")
llm = Llama(model_path="model_path", n_ctx=2048)  # Adjust the path as needed
print("Model loaded!")

def get_llama_response(prompt, max_tokens=32, stop=["Q:", "\n"]):
    # Use the LLaMA Python wrapper to get a response
    response = llm(f"Q:{prompt}? A: ", max_tokens=max_tokens, stop=stop, echo=True)
    # Extracting the generated text from the response
    if response and "choices" in response and len(response["choices"]) > 0:
        return response
    else:
        return "No response generated."

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    try:
        # Get the response from the LLaMA model
        response = get_llama_response(prompt)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # app.run(debug=True)  # Set debug=False for production
    app.run(debug=True, host='127.0.0.1', port=8080)
