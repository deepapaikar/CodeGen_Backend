# app.py
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user, login_user, logout_user, login_required
import autogen, re

app = Flask(__name__)
config_list = [
    {
        'model': 'gpt-3.5-turbo-1106',
        'api_key': '',
    }]
socketio = SocketIO(app)
@app.route('/')
def index():
    return render_template('frontend_runchat.html')
pattern = re.compile(r"You: (.+?)\nAgent: (.+?)(?=You:|$)", re.DOTALL)
def create_user_proxy_assistant():
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
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config={
            "cache_seed": 42,  # seed for caching and reproducibility
            "config_list": config_list,  # a list of OpenAI API configurations
            "temperature": 0,  # temperature for sampling
        },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
    )
    return user_proxy, assistant
user_proxys = {}
assistants = {}
@socketio.on('connect')
def handle_connect():
    join_room(request.sid)  
    user_proxys[request.sid], assistants[request.sid] = create_user_proxy_assistant()
    print('connect', request.sid)
@socketio.on('message')
def handle_message(message):
    print('receive message', message)
    try:
        user_input = message.get('content')
        user_proxy = user_proxys[request.sid]
        user_proxy.initiate_chat(assistants[request.sid], message=user_input,socket_room_id=request.sid)
        
        dialogue = user_proxy.get_stored_output()  # save dialogue for differenet user in dialogue
        matches = pattern.findall(dialogue)
        dialogue = [{"you": match[0], "agent": match[1]} for match in matches]
    except Exception as e:
        response = {"error": str(e)}
if __name__ == '__main__':
    socketio.run(app, debug=True,port=5002)
