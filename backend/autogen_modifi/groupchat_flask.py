import autogen
import networkx as nx
import matplotlib.pyplot as plt
from autogen.agentchat.groupchat import GroupChat
from autogen.agentchat.assistant_agent import AssistantAgent, Agent, UserProxyAgent, ConversableAgent
from autogen.agentchat.agent import Agent
from autogen.agentchat.contrib.llava_agent import llava_call
from autogen.agentchat.contrib.llava_agent import LLaVAAgent

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user, login_user, logout_user, login_required
import autogen, re
from flask_cors import CORS
from flask import Flask, request, render_template

import random
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
import logging
import sys
import random
from dataclasses import dataclass
import re
import autogen
import requests
import json
import os
from termcolor import colored
import replicate

logger = logging.getLogger(__name__)

# ----------------change groupchat.py's system prompt

class CustomGroupChat(GroupChat):
    def __init__(self, agents, messages, max_round=10):
        super().__init__(agents, messages, max_round)
        self.previous_speaker = None  # Keep track of the previous speaker


    def select_speaker(self, last_speaker: Agent, selector: ConversableAgent):
        """Select the next speaker."""
        if self.speaker_selection_method.lower() not in self._VALID_SPEAKER_SELECTION_METHODS:
            raise ValueError(
                f"GroupChat speaker_selection_method is set to '{self.speaker_selection_method}'. "
                f"It should be one of {self._VALID_SPEAKER_SELECTION_METHODS} (case insensitive). "
            )

        agents = self.agents
        n_agents = len(agents)
        # Warn if GroupChat is underpopulated
        if n_agents < 2:
            raise ValueError(
                f"GroupChat is underpopulated with {n_agents} agents. "
                "Please add more agents to the GroupChat or use direct communication instead."
            )
        elif n_agents == 2 and self.speaker_selection_method.lower() != "round_robin" and self.allow_repeat_speaker:
            logger.warning(
                f"GroupChat is underpopulated with {n_agents} agents. "
                "It is recommended to set speaker_selection_method to 'round_robin' or allow_repeat_speaker to False."
                "Or, use direct communication instead."
            )

        if self.func_call_filter and self.messages and "function_call" in self.messages[-1]:
            # find agents with the right function_map which contains the function name
            agents = [
                agent for agent in self.agents if agent.can_execute_function(self.messages[-1]["function_call"]["name"])
            ]
            if len(agents) == 1:
                # only one agent can execute the function
                return agents[0]
            elif not agents:
                # find all the agents with function_map
                agents = [agent for agent in self.agents if agent.function_map]
                if len(agents) == 1:
                    return agents[0]
                elif not agents:
                    raise ValueError(
                        f"No agent can execute the function {self.messages[-1]['name']}. "
                        "Please check the function_map of the agents."
                    )

        # remove the last speaker from the list to avoid selecting the same speaker if allow_repeat_speaker is False
        agents = agents if self.allow_repeat_speaker else [agent for agent in agents if agent != last_speaker]

        if self.speaker_selection_method.lower() == "manual":
            selected_agent = self.manual_select_speaker(agents)
            if selected_agent:
                return selected_agent
        elif self.speaker_selection_method.lower() == "round_robin":
            return self.next_agent(last_speaker, agents)
        elif self.speaker_selection_method.lower() == "random":
            return random.choice(agents)

        # auto speaker selection
        selector.update_system_message(self.select_speaker_msg(agents))
        final, name = selector.generate_oai_reply(
            self.messages
            + [
                {
                    "role": "system",
                    "content": f"Read the above conversation. If this question from user_proxy can be simply answer without any code and is the 1st time generate answer, please only return 'answer_A'. Otherwise, the question require code answer then select the next role from {['user_proxy', 'code_generator', 'plan_excutor', 'planner', 'code_proxy', 'critic']} to play. Only return the role.",
                }
            ]
        )
        if not final:
            # the LLM client is None, thus no reply is generated. Use round robin instead.
            return self.next_agent(last_speaker, agents)

        # If exactly one agent is mentioned, use it. Otherwise, leave the OAI response unmodified
        mentions = self._mentioned_agents(name, agents)
        if len(mentions) == 1:
            name = next(iter(mentions))
        else:
            logger.warning(
                f"GroupChat select_speaker failed to resolve the next speaker's name. This is because the speaker selection OAI call returned:\n{name}"
            )

        # Return the result
        try:
            return self.agent_by_name(name)
        except ValueError:
            return self.next_agent(last_speaker, agents)


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
def groupchat_a(config_list_gpt4):
    # ----------------------------------group members
    # ------------------------1. code team used for code planner and excution
    user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
    code_execution_config=False,
    socket_room_id = request.sid,
    )

    planner = autogen.AssistantAgent(
        name="Planner",
        system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
    The plan may involve an code_generator who can write code and a plan_excutor who doesn't write code.
    Explain the plan first. Be clear which step is performed by an code_generator, and which step is performed by a code_generator
    ''',
        llm_config=config_list_gpt4,
        socket_room_id = request.sid,
    )

    plan_excutor = autogen.AssistantAgent(
        name="plan_excutor",
        llm_config=config_list_gpt4,
        system_message="""plan_excutor. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code.""",
        socket_room_id = request.sid,
    )

    code_generator = autogen.AssistantAgent(
        name="code_generator",
        llm_config=config_list_gpt4,
        system_message='''code_generator. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the code_proxy.
    Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the code_proxy.
    If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
    ''',
        socket_room_id = request.sid,
    )

    code_proxy = autogen.UserProxyAgent(
        name="code_proxy",
        system_message="code_proxy. Execute the code written by the code_generator and report the result.",
        human_input_mode="NEVER",
        code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
        socket_room_id = request.sid,
    )

    critic = autogen.AssistantAgent(
        name="Critic",
        system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL.",
        llm_config=config_list_gpt4,
        socket_room_id = request.sid,
    )

    # ------------------------2. genral knowledge team used for general knowledge answering without code.

    answer_A = autogen.AssistantAgent(
        name="answer_A",
        system_message='answer_A, if code_generator,code_proxy,planner,critic did not give answer and only questions that do not require code, then answer the question and interact with Terminator_A to terminate the chat session',
        llm_config=config_list_gpt4,
        socket_room_id = request.sid,
    )
    Terminator_A = autogen.AssistantAgent(
        name="Terminator_A",
        system_message='Terminator_A, if code_generator,code_proxy,planner,critic did not give answer, only return "TERMINATE" to end the chat session, then interact with Terminator',
        llm_config=config_list_gpt4,
        socket_room_id = request.sid,
    )

    Terminator = autogen.UserProxyAgent(
    name="Terminator",
    system_message="Terminator, if code_generator,code_proxy,planner,critic did not give answer, help the Terminator_A to end chat",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith('"TERMINATE".'),
    code_execution_config=False,
    socket_room_id = request.sid,
    )

    # ------------------------3. llava mode to answer those image related questions
    image_agent = LLaVAAgent(
        name="image-explainer",
        max_consecutive_auto_reply=10,
        system_message="image-explainer, if question is about image, such as those messages include '<img ', then explain the image and interact with Terminator_A to terminate the chat session",
        llm_config={"config_list": llava_config_list, "temperature": 0.5, "max_new_tokens": 1000},
        socket_room_id = request.sid,
    )

    groupchat = GroupChat(agents=[user_proxy, code_generator, plan_excutor, planner, code_proxy, critic, Terminator, answer_A, Terminator_A, image_agent], messages=[], max_round=10)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=config_list_gpt4)

    return user_proxy, manager