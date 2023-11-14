import autogen #start importing the autogen lib


config_list = [{
    "api_type" : "open_ai",
    "api_base" : "http://localhost:1234/v1",
    "api_key" : "NULL"
}]

assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "seed": 42,  # seed for caching and reproducibility
        "config_list": config_list,  # a list of OpenAI API configurations
        "temperature": 0,  # temperature for sampling
        "request_timeout": 400, # timeout
    },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
)

# create a human UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10, 
    default_auto_reply="",
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "agents-workspace", # set the working directory for the agents to create files and execute
        "use_docker": False,  # set to True or image name like "python:3" to use docker
    },
)


# the assistant receives a message from the user_proxy, which contains the task description
user_proxy.initiate_chat(
    assistant,
    message="""Create a python program to find if a string is pallindrome or not.""",
)