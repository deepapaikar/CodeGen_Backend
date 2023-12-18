import autogen
from autogen.agentchat.groupchat import GroupChat
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.llava_agent import LLaVAAgent


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

os.environ["REPLICATE_API_TOKEN"] = "r8_JDmEHu1VGuJqwyKZ9QqBvIn5NTvIebm0nxxuH"
    
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
        system_message='''Planner. Suggest a plan and interact with ctitic to confirm this plan. Then give the plan to code_generator and plan_excutor to execute the plan. 
    The plan may involve an code_generator who can write code and a plan_excutor who doesn't write code.
    Explain the plan first. Be clear which step is performed by an code_generator, and which step is performed by a code_generator
    ''',
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
        system_message='''code_generator. You follow the suggested plan by Planner and Crtic. You  suggest python code (in a python coding block) or shell script (in a sh coding block)  to solve tasks. When using code, you must indicate the script type in the code block. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the code_proxy.
        If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the code_proxy.
        If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
        ''',
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
        system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL.",
        llm_config=config_list_gpt4,
        socket_room_id = resid,
    )

    # ------------------------2. genral knowledge team used for general knowledge answering without code.

    answer_A = autogen.AssistantAgent(
        name="answer_A",
        system_message='answer_A, if code_generator,code_proxy,planner,critic did not response and only questions that do not require code, then answer the question. Reply "TERMINATE" in the end when everything is done.',
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
                "client": chromadb.PersistentClient(path="./tmp/chromadb"),
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