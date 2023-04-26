"""Chrome-GPT: An AutoGPT agent that interacts with Chrome"""
import click

from chromegpt.main import run_chromegpt

@click.command()
@click.option("--task", "-t", help="The task to execute", required=True)
@click.option("--model", "-m", help="The model to use", default="gpt-3.5-turbo")
@click.option("--headless", help="Run in headless mode", is_flag=True)
@click.option("--verbose", "-v", help="Run in verbose mode", is_flag=True)
def main(task: str, model: str = "gpt-3.5-turbo", headless: bool = False, verbose: bool = False) -> str:
    """Run ChromeGPT: An AutoGPT agent that interacts with Chrome"""
    return run_chromegpt(task, model, headless, verbose)

if __name__ == "__main__":
    main()