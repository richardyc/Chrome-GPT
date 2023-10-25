"""Module for the AutoGPT agent. Optimized for GPT-4 use."""
from typing import List

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.experimental import AutoGPT
from langchain.experimental.autonomous_agents.autogpt.output_parser import (
    AutoGPTOutputParser,
)
from langchain.tools.human.tool import HumanInputRun

from chromegpt.agent.autogpt.prompt import AutoGPTPrompt
from chromegpt.agent.chromegpt_agent import ChromeGPTAgent
from chromegpt.agent.utils import get_agent_tools, get_vectorstore


class AutoGPTAgent(ChromeGPTAgent):
    """AutoGPT agent for ChromeGPT. Note that this agent is optimized for GPT-4 use."""

    def __init__(
        self, model: str = "gpt-4", verbose: bool = False, continuous: bool = True
    ) -> None:
        """Initialize the AutoGPTAgent."""
        self.agent = self._get_autogpt_agent(
            llm=ChatOpenAI(model_name=model, temperature=0),  # type: ignore
            verbose=verbose,
            human_in_the_loop=not continuous,
        )
        self.model = model

    def _get_autogpt_agent(
        self, llm: ChatOpenAI, verbose: bool, human_in_the_loop: bool = False
    ) -> AutoGPT:
        vectorstore = get_vectorstore()
        tools = get_agent_tools()
        ai_name = "Jarvis"

        prompt = AutoGPTPrompt(
            ai_name=ai_name,
            ai_role="Assistant",
            tools=tools,
            input_variables=["memory", "messages", "goals", "user_input"],
            token_counter=llm.get_num_tokens,
        )
        human_feedback_tool = HumanInputRun() if human_in_the_loop else None
        chain = LLMChain(llm=llm, prompt=prompt)
        agent = AutoGPT(
            ai_name,
            vectorstore.as_retriever(),  # type: ignore
            chain,
            AutoGPTOutputParser(),
            tools,
            feedback_tool=human_feedback_tool,
        )
        # Set verbose to be true
        agent.chain.verbose = verbose
        return agent

    def run(self, tasks: List[str]) -> str:
        return self.agent.run(tasks)
