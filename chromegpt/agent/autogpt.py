"""Module for the AutoGPT agent. Optimized for GPT-4 use."""
from typing import List
from chromegpt.agent.chromegpt_agent import ChromeGPTAgent
from langchain.experimental import AutoGPT
from langchain.chat_models import ChatOpenAI

from chromegpt.agent.utils import get_agent_tools, get_vectorstore

class AutoGPTAgent(ChromeGPTAgent):
    def __init__(self, model="gpt-4", verbose=False) -> None:
        """Initialize the ZeroShotAgent."""
        self.agent = self._get_autogpt_agent(llm=ChatOpenAI(model_name=model, temperature=0), verbose=verbose)
        self.model = model

    def _get_autogpt_agent(self, llm, verbose) -> AutoGPT:
        vectorstore = get_vectorstore()
        tools = get_agent_tools()
        agent = AutoGPT.from_llm_and_tools(
            ai_name="Jarvis",
            ai_role="Assistant",
            tools=tools,
            llm=llm,
            memory=vectorstore.as_retriever(), # type: ignore
            # human_in_the_loop=True
        )
        # Set verbose to be true
        agent.chain.verbose = verbose
        return agent

    def run(self, tasks: List[str]) -> str:
        return self.agent.run(tasks)
