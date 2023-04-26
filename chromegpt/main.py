
from chromegpt.agent.autogpt import AutoGPTAgent
from chromegpt.agent.zeroshot import BabyAGIAgent


def run_chromegpt(task: str, model: str = "gpt-3.5-turbo", headless: bool = False, verbose: bool = False) -> str:
    """Run ChromeGPT."""
    # setup agent
    # agent = AutoGPTAgent(model = model, verbose = verbose)
    agent = BabyAGIAgent(model = model, verbose = verbose)
    # run agent
    return agent.run([task])
    