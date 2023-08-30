from chromegpt.tools.selenium import SeleniumWrapper


def execute_with_driver(test_function):
    def wrapper(*args, **kwargs):
        try:
            client = SeleniumWrapper(headless=True)
            result = test_function(*args, **kwargs, client=client)
        finally:
            # release the driver
            del client
        return result

    return wrapper
