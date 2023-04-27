
from chromegpt.agent.autogpt import AutoGPTAgent
from chromegpt.agent.zeroshot import BabyAGIAgent, ZeroShotAgent


def run_chromegpt(task: str, model: str = "gpt-3.5-turbo", agent: str =  "zero-shot", headless: bool = False, verbose: bool = False) -> str:
    """Run ChromeGPT."""
    # setup agent
    if agent == "auto-gpt":
        agent = AutoGPTAgent(model = model, verbose = verbose)
    elif agent == "baby-agi":
        agent = BabyAGIAgent(model = model, verbose = verbose)
    elif agent == "zero-shot":
        agent = ZeroShotAgent(model = model, verbose = verbose)
    else:
        raise ValueError(f"Agent {agent} not found.")
    # run agent
    return agent.run([task])
    