from typing import Any, Callable

from chromegpt.tools.selenium import SeleniumWrapper


def execute_with_driver(test_function: Callable[[SeleniumWrapper], None]) -> Callable:
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            client = SeleniumWrapper(headless=True)
            test_function(client, *args, **kwargs)
        finally:
            # release the driver
            del client

    return wrapper
