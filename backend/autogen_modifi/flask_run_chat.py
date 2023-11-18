from flask import Flask, request, jsonify, send_from_directory
from threading import Thread
import autogen
import uuid
import os
import re
# from flask_cors import CORS

app = Flask(__name__)
# CORS(app)


# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def serve(path):
#     if path != "" and os.path.exists(app.static_folder + '/' + path):
#         return send_from_directory(app.static_folder, path)
#     else:
#         return send_from_directory(app.static_folder, 'index.html')
    


config_list = [
    {
        'model': 'gpt-4',
        'api_key': '<your api key>',
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

def format(message):
    # Splitting the original chat log into individual messages
    messages = message.split("--------------------------------------------------------------------------------")

    # Filtering out empty messages
    messages = [msg.strip() for msg in messages if msg.strip()]

    # Extracting and arranging messages in alternating order
    user_proxy_messages = [msg for msg in messages if "user_proxy (to assistant):" in msg]
    assistant_messages = [msg for msg in messages if "assistant (to user_proxy):" in msg]

    # Interleaving messages
    interleaved_messages = []
    for i in range(max(len(user_proxy_messages), len(assistant_messages))):
        if i < len(user_proxy_messages)& i!=0:
            interleaved_messages.append(user_proxy_messages[i].replace("user_proxy (to assistant):", ""))
        if i < len(assistant_messages):
            interleaved_messages.append(assistant_messages[i].replace("assistant (to user_proxy):", ""))

    # Formatting the interleaved messages
    reformatted_chat_log = "\n--------------------------------------------------------------------------------\n".join(interleaved_messages)
    return reformatted_chat_log

@app.route('/chat', methods=['POST'])
def chat():

    response_u = None
    response_a = None
    message_all=None

    try:
        data = request.json
        user_input = data.get('user_input')
        user_proxy.initiate_chat(assistant, message=user_input)
        response_u = user_proxy.get_stored_output()  # the originl output is a string
        response_a = assistant.get_stored_output()

        message_all=response_a+response_u
        formatted_message = format(message_all)

        # dialogue = user_proxy.get_stored_output()  # save dialogue for differenet user in dialogue
        # matches = pattern.findall(dialogue)
        # dialogue = [{"you": match[0], "agent": match[1]} for match in matches]
        
    except Exception as e:
        formatted_message = "Error occurred"
        formatted_message = str(e)
    return jsonify(formatted_message)



@app.route('/')
def index():
    return app.send_static_file('frontend_runchat.html')


if __name__ == '__main__':
    app.run(debug=True)
