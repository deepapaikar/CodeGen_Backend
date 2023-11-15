from flask import Flask, request, jsonify
from threading import Thread
import autogen
import uuid
import re

app = Flask(__name__)
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
        user_input = data.get('user_input')
        user_proxy.initiate_chat(assistant, message=user_input)
        response = user_proxy.get_stored_output()  # the originl output is a string

        dialogue = user_proxy.get_stored_output()  # save dialogue for differenet user in dialogue
        matches = pattern.findall(dialogue)
        dialogue = [{"you": match[0], "agent": match[1]} for match in matches]
        
    except Exception as e:
        response = {"error": str(e)}
    return jsonify(response)



@app.route('/')
def index():
    return app.send_static_file('frontend_runchat.html')


if __name__ == '__main__':
    app.run(debug=True)
