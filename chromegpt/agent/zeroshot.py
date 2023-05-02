"""Module for the zero shot agent. Optimized for GPT-3.5 use."""
import types
from typing import Any, Dict, List, Tuple

from langchain import LLMChain, PromptTemplate
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.agents.agent import AgentExecutor
from langchain.agents.mrkl.base import ZeroShotAgent as LangChainZeroShotAgent
from langchain.chat_models import ChatOpenAI
from langchain.experimental import BabyAGI
from langchain.schema import AgentAction
from langchain.tools.base import BaseTool

from chromegpt.agent.chromegpt_agent import ChromeGPTAgent
from chromegpt.agent.utils import get_agent_tools, get_vectorstore


def get_zeroshot_agent(llm: ChatOpenAI, verbose: bool = False) -> AgentExecutor:
    """Get the zero shot agent. Optimized for GPT-3.5 use."""
    tools = get_agent_tools()
    agent = initialize_agent(
        tools, llm, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=verbose
    )
    return agent


def _get_full_inputs(
    self: Any,
    intermediate_steps: List[Tuple[AgentAction, str]],
    **kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """Create the full inputs for the LLMChain from intermediate steps.
    Patched version limit to 5 intermediate steps.
    """
    thoughts = self._construct_scratchpad(
        intermediate_steps[-4:]
    )  # limit to 4 intermediate steps for GPT-3.5
    new_inputs = {"agent_scratchpad": thoughts, "stop": self._stop}
    full_inputs = {**kwargs, **new_inputs}
    return full_inputs


class ZeroShotAgent(ChromeGPTAgent):
    def __init__(self, model: str = "gpt-3.5-turbo", verbose: bool = False) -> None:
        """Initialize the ZeroShotAgent."""
        self.model = model
        self.agent = get_zeroshot_agent(
            llm=ChatOpenAI(model_name=model, temperature=0),  # type: ignore
            verbose=verbose,
        )
        self.agent.max_iterations = 30
        self.agent.agent.__dict__["get_full_inputs"] = types.MethodType(
            _get_full_inputs, self.agent.agent
        )

    def run(self, tasks: List[str]) -> str:
        return self.agent.run(" ".join(tasks))


class BabyAGIAgent(ChromeGPTAgent):
    def __init__(self, model: str = "gpt-3.5-turbo", verbose: bool = False) -> None:
        """Initialize the BabyAGIAgent."""
        self.model = model
        self.babyagi = self._get_baby_agi(verbose=verbose)

    def _get_todo_tool(self) -> Tool:
        todo_prompt = PromptTemplate.from_template(
            "You are a planner who is an expert at coming up "
            "with a todo list for a given objective. Come up "
            "with a todo list for this objective: {objective}"
        )
        todo_chain = LLMChain(
            llm=ChatOpenAI(model=self.model, temperature=0),  # type: ignore
            prompt=todo_prompt,
        )
        return Tool(
            name="TODO",
            func=todo_chain.run,
            description=(
                "useful for when you need to come up with todo lists. Input: an"
                " objective to create a todo list for. Output: a todo list for that"
                " objective. Please be very clear what the objective is!"
            ),
        )

    def _get_baby_agi(self, verbose: bool = False, max_iterations: int = 20) -> BabyAGI:
        """Get the zero shot agent. Optimized for GPT-3.5 use."""
        llm = ChatOpenAI(model_name=self.model, temperature=0)  # type: ignore
        tools = get_agent_tools()
        # Add ToDo tool for baby agi
        tools.append(self._get_todo_tool())
        agent = self._get_zero_shot_agent(llm=llm, verbose=verbose, tools=tools)
        vectorstore = get_vectorstore()
        baby_agi = BabyAGI.from_llm(
            llm=llm,
            vectorstore=vectorstore,  # type: ignore
            task_execution_chain=agent,
            verbose=verbose,
            max_iterations=max_iterations,  # type: ignore
        )
        return baby_agi

    def _get_zero_shot_agent(
        self, llm: ChatOpenAI, verbose: bool, tools: List[BaseTool]
    ) -> AgentExecutor:
        prefix = (
            "You are an AI who performs one task based on the "
            "following objective: {objective}. Take into account these "
            "previously completed tasks: {context}."
        )
        suffix = """Question: {task}
        {agent_scratchpad}"""
        prompt = LangChainZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["objective", "task", "context", "agent_scratchpad"],
        )
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        tool_names = [tool.name for tool in tools]
        agent = LangChainZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names)
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, max_iterations=4
        )
        return agent_executor

    def run(self, tasks: List[str]) -> str:
        return str(self.babyagi({"objective": " ".join(tasks)}))
