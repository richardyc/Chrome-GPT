"""Tool that calls Selenium."""
import json
import validators
import re
import time
from typing import List, Optional, Union
from pydantic import BaseModel, Field

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import urllib.parse


from chromegpt.tools.utils import get_all_text_elements, prettify_text, truncate_string_from_last_occurrence


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

    def google_search(self, query: str) -> str:
        safe_string = urllib.parse.quote_plus(query)
        # Go to website
        self.describe_website("https://www.google.com/search?q="+safe_string)

        # Scrape search results
        results = []
        search_results = self.driver.find_elements(By.CSS_SELECTOR, "#search .g")
        for index, result in enumerate(search_results, start=1):
            try:
                title_element = result.find_element(By.CSS_SELECTOR, "h3")
                link_element = result.find_element(By.CSS_SELECTOR, "a")
                
                title = title_element.text
                link = link_element.get_attribute("href")
                if title and link:
                    results.append({
                        "title": title,
                        "position": index,
                        "link": link,
                    })
            except Exception as e:
                continue
        return "Which url would you like to goto? Provide the full url starting with http or https: " + json.dumps(results)

    def describe_website(self, url: Optional[str] = None) -> str:
        """Describe the website."""
        output = ""
        if url:
            try:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(url)
            except Exception as e:
                return f"Cannot load website {url}. Make sure you input the correct and complete url starting with http:// or https://."
        # Extract main content
        time.sleep(2) # Wait for website to load
        try:
            main_content = self._get_website_main_content()
        except WebDriverException as e:
            return "Website still loading, please wait a few seconds and try again."
        if main_content:
            output += f"{main_content}\n"

        # Extract interactable components (buttons and links)
        interactable_content = self._get_interactable_elements()
        if interactable_content:
            output += f"{interactable_content}\n"

        # Extract form inputs
        form_fields = self._find_form_fields()
        if form_fields:
            output += "Text Input Fields: " + str(form_fields)
        return output

    def click_button_by_text(self, button_text: str) -> str:
        # check if the button text is url
        if validators.url(button_text):
            return self.describe_website(button_text)
        before_content = self.describe_website()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        # If there are string surrounded by double quotes, extract them
        if button_text.count('"') > 1:
            try:
                button_text = re.findall(r'"([^"]*)"', button_text)[0]
            except IndexError:
                # No text surrounded by double quotes
                pass
        try:
            buttons = self.driver.find_elements(By.XPATH, "//button")
            links = self.driver.find_elements(By.XPATH, "//a")

            elements = buttons + links

            if not elements:
                return "No interactable buttons found in the website. Try another website."

            selected_element = None
            for element in elements:
                text = prettify_text(element.text)
                if element.is_displayed() and element.is_enabled() and (text.lower() == button_text.lower() or (button_text.lower() in text.lower() and abs(len(button_text)-len(text)) < 50)):
                    selected_element = element
                    break
            if not selected_element:
                return f"No interactable element found with text: {button_text}. Double check the button text and try again."
            
            # Scroll the element into view and Click the element using JavaScript
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
            time.sleep(1)
            after_content = self.describe_website()
            if before_content == after_content:
                output = f"Clicked interactable element but nothing changed on the website."
            else:
                output = f"Clicked interactable element and the website changed. Now "
                output += self.describe_website()
            return output
        except WebDriverException as e:
            return f"Error clicking button with text '{button_text}', message: {e.msg}"

    def find_form_inputs(self, url: str) -> str:
        """Find form inputs on the website."""
        fields = self._find_form_fields(url)
        if fields:
            form_inputs = "Form Input Fields: " + str(fields)
        else:
            form_inputs = "No form inputs found on current page. Try another website."
        return form_inputs
    
    def _find_form_fields(self, url: Optional[str]=None) -> List[str]:
        """Find form fields on the website."""
        if url and url != self.driver.current_url and url.startswith("http"):
            try:
                self.driver.get(url)
                time.sleep(1)
            except WebDriverException as e:
                return f"Error loading url {url}, message: {e.msg}"
        fields = []
        for element in self.driver.find_elements(By.TAG_NAME, 'textarea') + self.driver.find_elements(By.TAG_NAME, 'input'):
            label_txt = element.get_attribute('name') or element.get_attribute('aria-label') or element.find_element(By.XPATH, "..").text
            if label_txt and "\n" not in label_txt and len(label_txt) < 100 and label_txt not in fields:
                fields.append(label_txt)
        return fields

    def fill_out_form(self, form_input: Union[str, dict[str, str]]) -> str:
        """fill out form by form field name and input name"""
        before_content = self.describe_website()
        filled_element = None
        if type(form_input) == str:
            # Clean up form input
            form_input = truncate_string_from_last_occurrence(form_input, "}")
            try:
                form_input = json.loads(form_input)
            except json.decoder.JSONDecodeError:
                return 'Invalid JSON input. Please check your input is JSON format and try again. Make sure to use double quotes for strings. Example input: {"email": "foo@bar.com","name": "foo bar"}'
        try:
            for element in self.driver.find_elements(By.TAG_NAME, 'textarea') + self.driver.find_elements(By.TAG_NAME, 'input'):
                label_txt = element.get_attribute('name') or element.get_attribute('aria-label') or element.find_element(By.XPATH, "..").text
                if label_txt:
                    for key in form_input.keys(): # type: ignore
                        if key.lower() == label_txt.lower() or (key.lower() in label_txt.lower() and len(label_txt) - len(key) < 10):
                            try:
                                # Scroll the element into view
                                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                                time.sleep(1)  # Allow some time for the page to settle
                                element.send_keys(form_input[key])
                                filled_element = element
                                break
                            except WebDriverException as e:
                                continue
            if not filled_element:
                return f"Cannot find form with input: {form_input.keys()}. Available form inputs: {self._find_form_fields()}"
            filled_element.send_keys(Keys.RETURN)
            after_content = self.describe_website()
            if before_content != after_content:
                return f"Successfully filled out form with input: {form_input}, website changed after filling out form. Now {after_content}"
            else:
                return f"Successfully filled out form with input: {form_input}, but website did not change after filling out form."
        except WebDriverException as e:
            print(e)
            return f"Error filling out form with input {form_input}, message: {e.msg}"

    def scroll(self, direction: str) -> str:
        # Get the height of the current window
        window_height = self.driver.execute_script('return window.innerHeight')
        if direction == "up":
            window_height = -window_height

        # Scroll by 1 window height
        self.driver.execute_script(f'window.scrollBy(0, {window_height})')
        
        return self.describe_website()

    def _get_website_main_content(self) -> str:
        texts = get_all_text_elements(self.driver)
        pretty_texts = [prettify_text(text) for text in texts]
        if not pretty_texts:
            return ""

        description = f"Current window displays the following contents, try scrolling up or down to view more: "
        description += ' '.join(pretty_texts)

        return description

    def _get_interactable_elements(self) -> str:
        # Extract interactable components (buttons and links)
        buttons = self.driver.find_elements(By.XPATH, "//button")
        links = self.driver.find_elements(By.XPATH, "//a")

        interactable_elements = buttons + links

        interactable_texts = []
        for element in interactable_elements:
            button_text = element.text.strip()
            button_text = prettify_text(button_text, 50)
            if button_text and button_text not in interactable_texts and element.is_displayed() and element.is_enabled():
                interactable_texts.append(button_text)

        if not interactable_texts:
            return ""

        interactable_output = f"Here are a list of buttons/links that you can click on the current window: {json.dumps(interactable_texts)}"
        return interactable_output

class GoogleSearchInput(BaseModel):
    """Google search input model."""
    query: str = Field(..., description="search query")

class DescribeWebsiteInput(BaseModel):
    """Describe website input model."""
    url: str = Field(..., description="full URL starting with http or https", example="https://www.google.com/")

class ClickButtonInput(BaseModel):
    """Click button input model."""
    button_text: str = Field(..., description="text of the button/link you want to click", example="Contact Us")

class FindFormInput(BaseModel):
    """Find form input input model."""
    url: str = Field(..., description="the current website url", example="https://www.google.com/")

class FillOutFormInput(BaseModel):
    """Fill out form input model."""
    form_input: str = Field(..., description="json formatted dictionary with the input fields and their values", example='{"email": "foo@bar.com","name": "foo bar"}')

class ScrollInput(BaseModel):
    """Scroll window."""
    direction: str = Field(..., description="direction to scroll, either 'up' or 'down'")