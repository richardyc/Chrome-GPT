import time
from typing import Any, Callable, List

from langchain.experimental.autonomous_agents.autogpt.prompt_generator import get_prompt
from langchain.prompts.chat import (
    BaseChatPromptTemplate,
)
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.tools.base import BaseTool
from langchain.vectorstores.base import VectorStoreRetriever
from pydantic import BaseModel


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

    def _calculate_tokens(self, msgs: List[BaseMessage]) -> int:
        """Calculate the number of tokens used in the messages."""
        return sum([self.token_counter(msg.content) for msg in msgs])

    def _format_misc_messages(self, **kwargs: Any) -> List[BaseMessage]:
        """Format misc requried messages, such as time and date."""
        base_prompt = SystemMessage(content=self.construct_full_prompt(kwargs["goals"]))
        time_prompt = SystemMessage(
            content=f"The current time and date is {time.strftime('%c')}"
        )
        return [base_prompt, time_prompt]

    def _format_last_action(self, **kwargs: Any) -> List[BaseMessage]:
        """Format last action."""
        previous_messages = kwargs["messages"]
        if len(previous_messages) < 1:
            # Threre are no actions yet
            return []
        last_action = SystemMessage(content=previous_messages[-1].content)
        return [last_action]

    def _format_prev_actions(
        self, token_limit: int, **kwargs: Any
    ) -> List[BaseMessage]:
        """Format previous actions."""
        previous_messages = kwargs["messages"]
        prev_actions: List[BaseMessage] = []
        if len(previous_messages) < 2:
            # Threre are no previous actions
            return []
        used_tokens = 0
        for msg in previous_messages[-2:][::-1]:
            if used_tokens + self.token_counter(msg.content) > token_limit:
                break
            prev_actions.append(SystemMessage(content=msg.content))
            used_tokens += self.token_counter(msg.content)
        return prev_actions

    def _format_memory_messages(
        self, token_limit: int, **kwargs: Any
    ) -> List[BaseMessage]:
        """Format memory messages."""
        messages: List[BaseMessage] = []
        memory: VectorStoreRetriever = kwargs["memory"]
        previous_messages = kwargs["messages"]
        content_format = "This reminds you of these events from your past:\n"
        relevant_docs = memory.get_relevant_documents(str(previous_messages[-10:]))
        relevant_memory = [d.page_content for d in relevant_docs]
        relevant_memory_tokens = sum(
            [self.token_counter(doc) for doc in relevant_memory]
        ) + self.token_counter(content_format)

        while len(relevant_memory) > 0:
            if relevant_memory_tokens < token_limit:
                break
            relevant_memory_tokens -= self.token_counter(relevant_memory[-1])
            relevant_memory = relevant_memory[:-1]
        if len(relevant_memory) > 0:
            memory_message = SystemMessage(
                content=f"{content_format}{relevant_memory}\n\n"
            )
            messages += [memory_message]
        return messages

    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        """Format messages for the agent to process."""
        messages = []
        # Format misc messages
        input_message = HumanMessage(content=kwargs["user_input"])
        misc_messages = self._format_misc_messages(**kwargs)
        used_tokens = self._calculate_tokens(misc_messages + [input_message])
        messages += misc_messages

        # Format last action msg
        last_action = self._format_last_action(**kwargs)
        used_tokens += self._calculate_tokens(last_action)

        tokens_left = self.send_token_limit - used_tokens
        if tokens_left > 0:
            memory_messages = self._format_memory_messages(tokens_left // 2, **kwargs)
            messages += memory_messages
            used_tokens += self._calculate_tokens(memory_messages)
            # HACK: This is a hack since GPT-3 doesn't seem to like previous actions
            # token_limit = self.send_token_limit - used_tokens
            # prev_actions = self._format_prev_actions(token_limit, **kwargs)
            # messages += prev_actions
        messages += last_action
        messages.append(input_message)
        return messages
