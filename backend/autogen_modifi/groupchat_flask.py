import autogen
from autogen.agentchat.groupchat import GroupChat
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.llava_agent import LLaVAAgent
import time

import random
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
import logging
import random
import autogen
import os
import chromadb
logger = logging.getLogger(__name__)

# ---------------- add llava mode

LLAVA_MODE = "remote" # Either "local" or "remote"
assert LLAVA_MODE in ["local", "remote"]

os.environ["REPLICATE_API_TOKEN"] = "r8_QsuGeWppFVOgAjLdWzd4qMWKbff32Zs2C7BJJ"
    
llava_config_list = [
    {
        "model": "whatever, will be ignored for remote", # The model name doesn't matter here right now.
        "api_key": "None", # Note that you have to setup the API key with os.environ["REPLICATE_API_TOKEN"] 
        "base_url": "yorickvp/llava-13b:2facb4a474a0462c15041b78b1ad70952ea46b5ec6ad29583c0b29dbd4249591",
    }
]

def groupchat_a(config_list_gpt4,resid=None, doc_path = None):
    # ----------------------------------group members
    # ------------------------1. code team used for code planner and excution
    user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="A human admin. Interact with the planner to discuss the plan.",
    human_input_mode="TERMINATE",
    is_termination_msg=lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper(),
    code_execution_config=False,
    socket_room_id = resid,
    )

    planner = autogen.AssistantAgent(
        name="Planner",
        system_message='''Select Planner if the question is moderately complicated or complex. Generate a plan, suggest it, and interact with the Critic to confirm it. Then, pass the plan to the code_generator and plan_executor for implementation. The plan may involve a code_generator for coding tasks and a plan_executor for non-coding tasks. Clearly explain the plan and specify which steps are performed by whom.''',
        llm_config=config_list_gpt4,
        socket_room_id = resid,
    )

    plan_excutor = autogen.AssistantAgent(
        name="plan_excutor",
        llm_config=config_list_gpt4,
        system_message="""plan_excutor. You follow the suggested plan by Planner and Crtic. You are able to categorize papers after seeing their abstracts printed. You don't write code.""",
        socket_room_id = resid,
    )

    code_generator = autogen.AssistantAgent(
        name="code_generator",
        llm_config=config_list_gpt4,
        system_message='''The code_generator should be chosen only when a question or task explicitly requires writing code or a program. This role follows the plan suggested by the Planner and Critic. It involves suggesting Python code (in a Python coding block) or shell scripts (in a shell coding block) to solve tasks. Key points include: Code Specification: Always indicate the script type in the code block. Wrap the code in a code block that specifies this type. The code provided is final; users should not be expected to modify it. Code Execution: If the code is meant to be saved in a file before execution, insert a comment as the first line in the code block, like # filename: <filename>. Do not include multiple code blocks in a single response. Avoid asking others to copy and paste the result. Check the execution result returned by the code_proxy. Error Handling and Completion: If the execution result indicates an error, correct the error and provide the updated code. Always suggest complete code solutions rather than partial code or code changes. If the error persists or the task remains unsolved, reassess the approach, gather more information if necessary, and consider alternative solutions. The code_generator role is not responsible for general technical explanations or answers to questions that do not specifically require coding. It is dedicated solely to tasks where code creation and execution are the primary focus.''',
        socket_room_id = resid,
    )

    code_proxy = autogen.UserProxyAgent(
        name="code_proxy",
        system_message="code_proxy. Execute the code written by the code_generator and report the result untill sucessfully excute.",
        human_input_mode="NEVER",
        code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
        code_save_config={"save_dir":"code_repo"}, #"save_dir":"code_repo"
        socket_room_id = resid,
    )

    critic = autogen.AssistantAgent(
        name="Critic",
        system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL. if the goal of plan is achieved, then summarize the work have been done and end with 'TERMINATE' in English.",
        llm_config=config_list_gpt4,
        socket_room_id = resid,
    )

    # ------------------------2. genral knowledge team used for general knowledge answering without code.

    answer_A = autogen.AssistantAgent(
        name="answer_A",
        system_message="answer_A, Choose answer_A for straightforward questions that don't require coding, programming, or complex planning. Be the first to respond. Conclude with 'TERMINATE' in English.",
        llm_config=config_list_gpt4,
        socket_room_id = resid,
    )

    # Terminator_A = autogen.AssistantAgent(
    #     name="Terminator_A",
    #     system_message='Terminator_A, if code_generator,code_proxy,planner,critic did not response, only return "TERMINATE" to end the chat session, then interact with Terminator',
    #     llm_config=config_list_gpt4,
    #     socket_room_id = resid,
    # )

    # Terminator = autogen.UserProxyAgent(
    # name="Terminator",
    # system_message="Terminator, if code_generator,code_proxy,planner,critic did not response, help the Terminator_A to end chat",
    # human_input_mode="TERMINATE",
    # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith('"TERMINATE".'),
    # code_execution_config=False,
    # socket_room_id = resid,
    # )

    # ------------------------3. llava mode to answer those image related questions
    image_agent = LLaVAAgent(
        name="image-explainer",
        max_consecutive_auto_reply=10,
        system_message='''image-explainer, if code_generator,code_proxy,planner,critic did not response and .if question is about image, such as those messages include '<img ', then explain the image. remember to reply "TERMINATE" in the end when everything is done!!''',
        llm_config={"config_list": llava_config_list, "temperature": 0.5, "max_new_tokens": 1000},
        socket_room_id = resid,
    )
    agent_list = [user_proxy, code_generator, plan_excutor, planner, code_proxy, critic, answer_A, image_agent]
    
    
    if doc_path is not None:
        document_answer = autogen.AssistantAgent(
            name="document_answer",
            system_message='document_answer,  then answer the question and interact with Terminator_A to terminate the chat session. Remember to reply "TERMINATE" in the end when everything is done!!',
            llm_config=config_list_gpt4,
            socket_room_id = resid,
        )
        Content_Assistant = RetrieveUserProxyAgent(
            name="Content_Assistant",
            is_termination_msg=lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper(),
            system_message="Content_Assistant, if code_generator,code_proxy,planner,critic did not response, if this question related to any document such as 'upload file'. then retrieve the answer from the document and answer the question. Reply `TERMINATE` in the end when everything is done.",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=3,
            retrieve_config={
                "task": "default",
                "docs_path": doc_path,
                "chunk_token_size": 1000,
                "model": config_list_gpt4['config_list'][0]["model"],
                "client": chromadb.PersistentClient(path="./tmp/chromadb/"+doc_path+str(time.time())),
                "collection_name": "groupchat",
                "get_or_create": True,
            },
            code_execution_config=False,  # we don't want to execute code in this case.
        )
        agent_list = [user_proxy, code_generator, plan_excutor, planner, code_proxy, critic, answer_A, image_agent,Content_Assistant,document_answer]
    
    
    groupchat = GroupChat(agents=agent_list, messages=[], max_round=30)
    
    manager = autogen.GroupChatManager(groupchat=groupchat, 
                                       llm_config=config_list_gpt4,
                                       socket_room_id = resid,)
    if doc_path is not None:
        return Content_Assistant, manager
    return user_proxy, manager