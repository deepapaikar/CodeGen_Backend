import sys
# app.py
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user, login_user, logout_user, login_required
import autogen, re
from flask_cors import CORS
from groupchat_flask import groupchat_a
import base64
import os
from openai import OpenAI
app = Flask(__name__)
CORS(app, supports_credentials=True)


#------------------add temp dir
temp_dir = './tmp/'
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
    
# ---------------- gpt config
# The default config list in notebook.
config_list = [
    {
        #-----gpt----------
        'model': 'gpt-4-1106-preview',
        'api_key': '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',
    }]
# ---------------- check api key
def check_openai_api_key(api_key):
    client = OpenAI(
        api_key=api_key,
    )
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
        )
        res = True
    except Exception as e:
        print(e)
        res = False
    return res
check_result = check_openai_api_key(config_list[0]['api_key'])
if not check_result:
    raise Exception("Please set OPENAI_API_KEY environment variable to a valid API key.")

config_list_gpt4 = {
    "cache_seed": 42,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}

socketio = SocketIO(app, cors_allowed_origins='*')
@app.route('/')
def index():
    return render_template('frontend_runchat.html')

pattern = re.compile(r"You: (.+?)\nAgent: (.+?)(?=You:|$)", re.DOTALL)

user_proxys = {}
assistants = {}
file_dict = {}

@socketio.on('file-upload')
def handle_file_upload(json):
    print('receive file from', request.sid)
    print('receive file:' + json['name'])
    file_data = base64.b64decode(json['data'])
    file_name = json['name']
    save_path = os.path.join(temp_dir, file_name)  # Specify your directory path
    file_dict[request.sid] = save_path
    with open(save_path, 'wb') as file:
        file.write(file_data)
    user_proxys[request.sid], assistants[request.sid] = groupchat_a(config_list_gpt4,request.sid,doc_path=file_dict[request.sid])
    print('agent created')
    return 'File uploaded successfully'
@socketio.on('connect')

def handle_connect():
    join_room(request.sid)
    user_proxys[request.sid], assistants[request.sid] = groupchat_a(config_list_gpt4,request.sid)
    print('connect', request.sid)

# SocketIO event for updating API key
@socketio.on('update_api_key')
def handle_update_api_key(message):
    new_api_key = message['api_key']
    # Here we update the first configuration's API key
    config_list[0]['api_key'] = new_api_key
    print('API Key updated:', config_list[0]['api_key'])
    # Add any other logic you need after updating the key


@socketio.on('message')
def handle_message(message):
    print('receive message', message)
    try:
        user_input = message.get('content')
        user_proxy = user_proxys[request.sid]
        # ----xin add
        if user_proxy.name == "Content_Assistant":
            user_proxy.initiate_chat(assistants[request.sid], problem=user_input,clear_history=False)
        else:
            user_proxy.initiate_chat(assistants[request.sid], message=user_input, clear_history=False)
        # ----xin add
        dialogue = user_proxy.get_stored_output()  # save dialogue for differenet user in dialogue
        matches = pattern.findall(dialogue)
        dialogue = [{"you": match[0], "agent": match[1]} for match in matches]
    except Exception as e:
        response = {"error": str(e)}
        print(response)

if __name__ == '__main__':
    socketio.run(app, debug=False,port=5003)
