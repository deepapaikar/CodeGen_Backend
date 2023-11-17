from flask import Flask, request, jsonify, send_from_directory
from threading import Thread
import autogen
import uuid
import os
import re
from flask_cors import CORS

# TODO run the "npm run build" to generate the static files and change the location
app = Flask(__name__,static_folder='../../frontend/build')
# CORS(app)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
    

config_list = [
    {
        'model': 'gpt-4',
        'api_key': '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',
    }]
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "cache_seed": 42,  # seed for caching and reproducibility
        "config_list": config_list,  # a list of OpenAI API configurations
        "temperature": 0,  # temperature for sampling
    },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
)
# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,  # set to True or image name like "python:3" to use docker
    },
)

pattern = re.compile(r"You: (.+?)\nAgent: (.+?)(?=You:|$)", re.DOTALL)


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('msg')
        user_proxy.initiate_chat(assistant, message=user_input)
        response = user_proxy.get_stored_output()  # the originl output is a string

        dialogue = user_proxy.get_stored_output()  # save dialogue for differenet user in dialogue
        matches = pattern.findall(dialogue)
        dialogue = [{"you": match[0], "agent": match[1]} for match in matches]
        
    except Exception as e:
        response = {"error": str(e)}
    return jsonify(response)



# @app.route('/')
# def index():
#     return app.send_static_file('frontend_runchat.html')


if __name__ == '__main__':
    app.run(debug=True)
