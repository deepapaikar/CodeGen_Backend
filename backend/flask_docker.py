from flask import Flask, request, jsonify
import docker
import uuid

app = Flask(__name__)
client = docker.from_env()

@app.route('/execute_code', methods=['POST'])
def execute_code():
    code = request.json['code']
    container_name = f"code_runner_{uuid.uuid4()}"
    try:
        docker_command = f"python -c \"{code}\""
        print("Executing in Docker:", docker_command)

        container = client.containers.run("python:3.8", command=f"python -c \"{code}\"",
                                          name=container_name, detach=True)
        container.wait()

        logs = container.logs(stream=False, stdout=True, stderr=True)
        
        output = logs.decode('utf-8')
        print("Container logs:", output)
        
        return jsonify({"output": logs.decode('utf-8')})
    except Exception as e:

        print("Error:", str(e))
        return jsonify({"error": str(e)})
    
    
@app.route('/')
def index():
    return app.send_static_file('frontend.html')


if __name__ == '__main__':
    app.run(debug=True)