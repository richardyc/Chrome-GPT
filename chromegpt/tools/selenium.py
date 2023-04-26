"""Tool that calls Selenium."""
import json
import re
import time
from typing import List, Optional, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains


from chromegpt.tools.utils import get_all_text_elements, prettify_text


class SeleniumWrapper:
    """Wrapper around Selenium.

    To use, you should have the ``selenium`` python package installed.

    Example:
        .. code-block:: python

            from langchain import SeleniumWrapper
            selenium = SeleniumWrapper()
    """

    def __init__(self, headless: bool=False) -> None:
        """Initialize Selenium and start interactive session."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        else:
            chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)

    def __del__(self) -> None:
        """Close Selenium session."""
        self.driver.close()

    def describe_website(self, url: Optional[str] = None) -> str:
        """Describe the website."""
        output = ""
        if url:
            try:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(url)
                time.sleep(2)
            except Exception as e:
                return f"Cannot load website {url}. Make sure you have the correct and complete url."
        # Extract main content
        main_content = self._get_website_main_content()
        if main_content:
            output += f"{main_content}\n"

        # Extract interactable components (buttons and links)
        interactable_content = self._get_interactable_elements()
        if interactable_content:
            output += f"{interactable_content}\n"

        # Extract form inputs
        if self.driver.find_elements(By.TAG_NAME, 'input'):
            output += f"Found form inputs on current page. Use find_form function to get the input form details.\n"

        return output

    def click_button_by_text(self, button_text: str) -> str:
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(1)
        try:
            buttons = self.driver.find_elements(By.XPATH, "//button")
            links = self.driver.find_elements(By.XPATH, "//a")

            elements = buttons + links

            if not elements:
                return "No interactable buttons found in the website. Try another website."

            selected_element = None
            if "button" in button_text.lower():
                button_text = button_text.lower().replace("button", "").strip()
            if "link" in button_text.lower():
                button_text = button_text.lower().replace("link", "").strip()
            # If there are string surrounded by double quotes, extract them
            if '"' in button_text:
                try:
                    button_text = re.findall(r'"([^"]*)"', button_text)[0]
                except IndexError:
                    # No text surrounded by double quotes
                    pass
            for element in elements:
                text = prettify_text(element.text)
                if text.lower() == button_text.lower() or button_text.lower() in text.lower():
                    selected_element = element
                    break
            if not selected_element:
                return f"No interactable element found with text: {button_text}. Double check the button text and try again."
            
            # Scroll the element into view
            self.driver.execute_script("arguments[0].scrollIntoView();", selected_element)
            time.sleep(1)  # Allow some time for the page to settle
            
            # Click the element using JavaScript
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
            # self.driver.execute_script("arguments[0].click();", selected_element)
            output = f"Clicked interactable element with text: {button_text}\n"
            output += self.describe_website()
            return output
        except WebDriverException as e:
            return f"Error clicking button with text '{button_text}', message: {e.msg}"

    def find_form_inputs(self, url: str) -> str:
        """Find form inputs on the website."""
        if url != self.driver.current_url:
            self.driver.get(url)
            time.sleep(1)
        fields = ""
        for element in self.driver.find_elements(By.TAG_NAME, 'input'):
            label_txt = element.find_element(By.XPATH, "..")
            if label_txt.text and "\n" not in label_txt.text and len(label_txt.text) < 50:
                fields += f"{label_txt.text}, "
        if fields:
            form_inputs = "Form Input Fields: " + fields
        else:
            form_inputs = "No form inputs found on current page. Try another website."
        return form_inputs
    
    def fill_out_form(self, form_input: Union[str, dict[str, str]]) -> str:
        """fill out form by form field name and input name"""
        filled = False
        if type(form_input) == str:
            form_input = json.loads(form_input)
        try:
            for element in self.driver.find_elements(By.TAG_NAME, 'input'):
                label_txt = element.find_element(By.XPATH, "..")
                if label_txt.text:
                    for key in form_input.keys(): # type: ignore
                        if key.lower() in label_txt.text.lower() and len(label_txt.text) - len(key) < 10:
                            # Scroll the element into view
                            self.driver.execute_script("arguments[0].scrollIntoView();", element)
                            time.sleep(1)  # Allow some time for the page to settle
                            element.send_keys(form_input[key])
                            filled = True
                            break
            if not filled:
                return f"Cannot find form with input: {form_input.keys()}."
            return f"Successfully filled out form with input: {form_input}"
        except WebDriverException as e:
            return f"Error filling out form with input {form_input}, message: {e.msg}"

    def _get_website_main_content(self) -> str:
        texts = get_all_text_elements(self.driver)
        pretty_texts = [prettify_text(text) for text in texts]
        if not pretty_texts:
            return ""

        description = "The website displays the following contents: "
        description += '\n'.join(pretty_texts)

        return description

    def _get_interactable_elements(self) -> str:
        # Extract interactable components (buttons and links)
        buttons = self.driver.find_elements(By.XPATH, "//button")
        links = self.driver.find_elements(By.XPATH, "//a")

        interactable_elements = buttons + links

        interactable_texts = []
        for element in interactable_elements:
            button_text = element.text.strip()
            if button_text and button_text not in interactable_texts:
                button_text = prettify_text(button_text)
                interactable_texts.append(button_text)

        if not interactable_texts:
            return ""

        interactable_output = f"Here are a list of buttons/links that you can click: {json.dumps(interactable_texts)}"
        return interactable_output