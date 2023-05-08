from random import randint
from typing import Optional

from langchain import OpenAI, PromptTemplate

from reworkd_platform.settings import settings
from reworkd_platform.web.api.agent.model_settings import ModelSettings

GPT_35_TURBO = "gpt-3.5-turbo"


def get_server_side_key() -> str:
    keys = [key.strip() for key in
            (settings.openai_api_key or "").split(",")
            if key.strip()]
    return keys[randint(0, len(keys) - 1)] if keys else ""


def create_model(model_settings: Optional[ModelSettings]) -> OpenAI:
    _model_settings = model_settings
    if not model_settings or not model_settings.customApiKey:
        _model_settings = None
    return OpenAI(
        openAIApiKey=_model_settings.customApiKey or get_server_side_key(),
        temperature=_model_settings.customTemperature or 0.9,
        modelName=_model_settings.customModelName or GPT_35_TURBO,
        maxTokens=_model_settings.maxTokens or 400
    )


start_goal_prompt = PromptTemplate(
    template="""You are a task creation AI called AgentGPT. You must answer in the "{
    language}" language. You are not a part of any system or device. You have the
    following objective "{goal}". Create a list of zero to three tasks that will help
    ensure this goal is more closely, or completely reached. You have access to
    google search for tasks that require current events or small searches. Return the
    response as a formatted ARRAY of strings that can be used in JSON.parse().
    Example: ["{{TASK-1}}", "{{TASK-2}}"].""",
    input_variables=["goal", "language"]
)

analyze_task_prompt = PromptTemplate(
    template="""You have the following higher level objective "{goal}". You currently
    are focusing on the following task: "{task}". Based on this information, evaluate
    what the best action to take is strictly from the list of actions: {actions}. You
    should use 'search' only for research about current events where "arg" is a
    simple clear search query based on the task only. Use "reason" for all other
    actions. Return the response as an object of the form {{ "action": "string",
    "arg": "string" }} that can be used in JSON.parse() and NOTHING ELSE.""",
    input_variables=["goal", "actions", "task"]
)

execute_task_prompt = PromptTemplate(
    template="""You are AgentGPT. You must answer in the "{language}" language. Given
    the following overall objective `{goal}` and the following sub-task, `{task}`.
    Perform the task.""",
    input_variables=["goal", "language", "task"]
)

create_tasks_prompt = PromptTemplate(
    template="""You are an AI task creation agent. You must answer in the "{
    language}" language. You have the following objective `{goal}`. You have the
    following incomplete tasks `{tasks}` and have just executed the following task `{
    lastTask}` and received the following result `{result}`. Based on this, create a
    new task to be completed by your AI system ONLY IF NEEDED such that your goal is
    more closely reached or completely reached. Return the response as an array of
    strings that can be used in JSON.parse() and NOTHING ELSE.""",
    input_variables=["goal", "language", "tasks", "lastTask", "result"]
)

summarize_search_snippets = PromptTemplate(
    template="""Summarize the following snippets "{snippets}" from google search
    results filling in information where necessary. This summary should answer the
    following query: "{query}" with the following goal "{goal}" in mind. Return the
    summary as a string. Do not show you are summarizing.""",
    input_variables=["goal", "query", "snippets"]
)