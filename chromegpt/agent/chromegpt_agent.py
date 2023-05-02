from abc import ABC, abstractmethod
from typing import List


class ChromeGPTAgent(ABC):
    """Abstract class for ChromeGPT agents."""

    model: str
    verbose: bool = False

    @abstractmethod
    def run(self, tasks: List[str]) -> str:
        """Take in a list of tasks and return executed result."""
