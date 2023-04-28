import time
from typing import Any, Callable, List

from pydantic import BaseModel

from langchain.experimental.autonomous_agents.autogpt.prompt_generator import get_prompt
from langchain.prompts.chat import (
    BaseChatPromptTemplate,
)
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.tools.base import BaseTool
from langchain.vectorstores.base import VectorStoreRetriever


class AutoGPTPrompt(BaseChatPromptTemplate, BaseModel):
    ai_name: str
    ai_role: str
    tools: List[BaseTool]
    token_counter: Callable[[str], int]
    send_token_limit: int = 4196

    def construct_full_prompt(self, goals: List[str]) -> str:
        prompt_start = (
            "Your decisions must always be made independently "
            "without seeking user assistance.\n"
            "Play to your strengths as an LLM and pursue simple "
            "strategies with no legal complications.\n"
            "If you have completed all your tasks, make sure to "
            'use the "finish" command.'
        )
        # Construct full prompt
        full_prompt = (
            f"You are {self.ai_name}, {self.ai_role}\n{prompt_start}\n\nGOALS:\n\n"
        )
        for i, goal in enumerate(goals):
            full_prompt += f"{i+1}. {goal}\n"

        full_prompt += f"\n\n{get_prompt(self.tools)}"
        return full_prompt

    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        base_prompt = SystemMessage(content=self.construct_full_prompt(kwargs["goals"]))
        time_prompt = SystemMessage(
            content=f"The current time and date is {time.strftime('%c')}"
        )
        used_tokens = self.token_counter(base_prompt.content) + self.token_counter(
            time_prompt.content
        )
        memory: VectorStoreRetriever = kwargs["memory"]
        previous_messages = kwargs["messages"]
        prev_context = ""
        if len(previous_messages) > 0:
            prev_context = previous_messages[-1].content
        relevant_docs = memory.get_relevant_documents(prev_context) # last step
        relevant_memory = [d.page_content for d in relevant_docs]
        relevant_memory_tokens = sum(
            [self.token_counter(doc) for doc in relevant_memory]
        )
        # Leave enough room for the last system action
        if len(previous_messages) > 0:
            last_system_messages = []
            last_system_actions_tokens = 0
            for msg in previous_messages[-3:][::-1]:
                last_system_actions_tokens += len(msg.content)
                # If msg itself is too long, we turncate it
                if len(msg.content) > self.send_token_limit - 200:
                    msg.content = msg.content[: self.send_token_limit - 200]
                last_system_messages.append(msg)
                if used_tokens + relevant_memory_tokens + last_system_actions_tokens < self.send_token_limit - 200:
                    break
                # HACK: currently only return last system msg due to poor performance
                # break
        else:
            last_system_actions_tokens = 0
            last_system_messages = []

        while len(relevant_memory) > 0:
            # 200 is arbitrary, but we want to leave enough room for misc tokens
            if used_tokens + relevant_memory_tokens + last_system_actions_tokens < self.send_token_limit - 200:
                break
            relevant_memory = relevant_memory[:-1]
            relevant_memory_tokens = sum(
                [self.token_counter(doc) for doc in relevant_memory]
            )
        if len(relevant_memory) > 0:
            content_format = (
                f"This reminds you of these events "
                f"from your past:\n{relevant_memory}\n\n"
            )
            memory_message = SystemMessage(content=content_format)
            used_tokens += len(memory_message.content)
        input_message = HumanMessage(content=kwargs["user_input"])
        messages: List[BaseMessage] = [base_prompt, time_prompt]
        if len(relevant_memory) > 0:
            messages += [memory_message]
        messages += last_system_messages
        messages.append(input_message)

        return messages
