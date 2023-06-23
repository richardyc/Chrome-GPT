"""Tool that calls Selenium."""
import json
import re
import time
import urllib.parse
from typing import Any, Dict, List, Optional

import validators
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from selenium import webdriver
from selenium.common.exceptions import (
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from chromegpt.tools.utils import (
    find_parent_element_text,
    get_all_text_elements,
    prettify_text,
    truncate_string_from_last_occurrence,
)


class SeleniumWrapper:
    """Wrapper around Selenium.

    To use, you should have the ``selenium`` python package installed.

    Example:
        .. code-block:: python

            from langchain import SeleniumWrapper
            selenium = SeleniumWrapper()
    """

    def __init__(self, headless: bool = False) -> None:
        """Initialize Selenium and start interactive session."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        else:
            chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)  # Wait 5 seconds for elements to load

    def __del__(self) -> None:
        """Close Selenium session."""
        self.driver.close()

    def previous_webpage(self) -> str:
        """Go back in browser history."""
        self.driver.back()
        return self.describe_website()

    def google_search(self, query: str) -> str:
        safe_string = urllib.parse.quote_plus(query)
        url = "https://www.google.com/search?q=" + safe_string
        # Go to website
        try:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(url)
        except Exception:
            return f"Cannot load website {url}. Try again later."

        # Scrape search results
        results = self._get_google_search_results()
        return (
            "Which url would you like to goto? Provide the full url starting with http"
            " or https to goto: "
            + json.dumps(results)
        )

    def _get_google_search_results(self) -> List[Dict[str, Any]]:
        # Scrape search results
        results = []
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        search_results = soup.find_all("div", class_="g")
        for _, result in enumerate(search_results, start=1):
            if result.find("a") and result.find("h3"):
                title_element = result.find("h3")
                link_element = result.find("a")

                title = title_element.get_text()
                link = link_element.get("href")
                if title and link:
                    results.append(
                        {
                            "title": title,
                            "link": link,
                        }
                    )
        return results

    def describe_website(self, url: Optional[str] = None) -> str:
        """Describe the website."""
        output = ""
        if url:
            try:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(url)
            except Exception:
                return (
                    f"Cannot load website {url}. Make sure you input the correct and"
                    " complete url starting with http:// or https://."
                )

        # Let driver wait for website to load
        time.sleep(1)  # Wait for website to load

        try:
            # Extract main content
            main_content = self._get_website_main_content()
        except WebDriverException:
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
            output += (
                "You can input text in these fields using fill_form function: "
                + form_fields
            )
        return output

    def click_button_by_text(self, button_text: str) -> str:
        # check if the button text is url
        if validators.url(button_text):
            return self.describe_website(button_text)
        # If it is google search, then fetch link from google
        if self.driver.current_url.startswith("https://www.google.com/search"):
            google_search_results = self._get_google_search_results()
            for result in google_search_results:
                if button_text.lower() in result["title"].lower():
                    return self.describe_website(result["link"])
        self.driver.switch_to.window(self.driver.window_handles[-1])
        # If there are string surrounded by double quotes, extract them
        if button_text.count('"') > 1:
            try:
                button_text = re.findall(r'"([^"]*)"', button_text)[0]
            except IndexError:
                # No text surrounded by double quotes
                pass
        try:
            elements = self.driver.find_elements(
                By.XPATH,
                "//button | //div[@role='button'] | //a | //input[@type='checkbox']",
            )

            if not elements:
                return (
                    "No interactable buttons found in the website. Try another website."
                )

            selected_element = None
            all_buttons = []
            for element in elements:
                text = find_parent_element_text(element)
                button_text = prettify_text(button_text)
                if (
                    element.is_displayed()
                    and element.is_enabled()
                    and (
                        text == button_text
                        or (
                            button_text in text
                            and abs(len(text) - len(button_text)) < 50
                        )
                    )
                ):
                    selected_element = element
                    if text and text not in all_buttons:
                        all_buttons.append(text)
                    break
            if not selected_element:
                return (
                    f"No interactable element found with text: {button_text}. Double"
                    " check the button text and try again. Available buttons:"
                    f" {json.dumps(all_buttons)}"
                )

            # Scroll the element into view and Click the element using JavaScript
            before_content = self.describe_website()
            actions = ActionChains(self.driver)
            actions.move_to_element(selected_element).click().perform()
            after_content = self.describe_website()
            if before_content == after_content:
                output = (
                    "Clicked interactable element but nothing changed on the website."
                )
            else:
                output = "Clicked interactable element and the website changed. Now "
                output += self.describe_website()
            return output
        except WebDriverException as e:
            return f"Error clicking button with text '{button_text}', message: {e.msg}"

    def find_form_inputs(self, url: Optional[str] = None) -> str:
        """Find form inputs on the website."""
        fields = self._find_form_fields(url)
        if fields:
            form_inputs = "Available Form Input Fields: " + fields
        else:
            form_inputs = "No form inputs found on current page. Try another website."
        return form_inputs

    def _find_form_fields(self, url: Optional[str] = None) -> str:
        """Find form fields on the website."""
        if url and url != self.driver.current_url and url.startswith("http"):
            try:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(url)
                # Let driver wait for website to load
                time.sleep(1)  # Wait for website to load
            except WebDriverException as e:
                return f"Error loading url {url}, message: {e.msg}"
        fields = []
        for element in self.driver.find_elements(By.XPATH, "//textarea | //input"):
            label_txt = (
                element.get_attribute("name")
                or element.get_attribute("aria-label")
                or find_parent_element_text(element)
            )
            if (
                label_txt
                and "\n" not in label_txt
                and len(label_txt) < 100
                and label_txt not in fields
            ):
                label_txt = prettify_text(label_txt)
                fields.append(label_txt)
        return str(fields)

    def fill_out_form(self, form_input: Optional[str] = None, **kwargs: Any) -> str:
        """fill out form by form field name and input name"""
        filled_element = None
        if form_input and type(form_input) == str:
            # Clean up form input
            form_input_str = truncate_string_from_last_occurrence(
                string=form_input, character="}"  # type: ignore
            )
            try:
                form_input = json.loads(form_input_str)
            except json.decoder.JSONDecodeError:
                return (
                    "Invalid JSON input. Please check your input is JSON format and try"
                    " again. Make sure to use double quotes for strings. Example input:"
                    ' {"email": "foo@bar.com","name": "foo bar"}'
                )
        elif not form_input:
            form_input = kwargs  # type: ignore
        try:
            for element in self.driver.find_elements(By.XPATH, "//textarea | //input"):
                label_txt = (
                    element.get_attribute("name")
                    or element.get_attribute("aria-label")
                    or find_parent_element_text(element)
                )
                if label_txt:
                    label_txt = prettify_text(label_txt)
                    for key in form_input.keys():  # type: ignore
                        if prettify_text(key) == label_txt:
                            # Scroll the element into view
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView();", element
                            )
                            time.sleep(0.5)  # Allow some time for the page to settle
                            try:
                                # Try clearing the input field
                                element.send_keys(Keys.CONTROL + "a")
                                element.send_keys(Keys.DELETE)
                                element.clear()
                            except WebDriverException:
                                pass
                            element.send_keys(form_input[key])  # type: ignore
                            filled_element = element
                            break
            if not filled_element:
                return (
                    f"Cannot find form with input: {form_input.keys()}."  # type: ignore
                    f" Available form inputs: {self._find_form_fields()}"
                )
            before_content = self.describe_website()
            filled_element.send_keys(Keys.RETURN)
            after_content = self.describe_website()
            if before_content != after_content:
                return (
                    f"Successfully filled out form with input: {form_input}, website"
                    f" changed after filling out form. Now {after_content}"
                )
            else:
                return (
                    f"Successfully filled out form with input: {form_input}, but"
                    " website did not change after filling out form."
                )
        except WebDriverException as e:
            print(e)
            return f"Error filling out form with input {form_input}, message: {e.msg}"

    def scroll(self, direction: str) -> str:
        # Get the height of the current window
        window_height = self.driver.execute_script("return window.innerHeight")
        if direction == "up":
            window_height = -window_height

        # Scroll by 1 window height
        self.driver.execute_script(f"window.scrollBy(0, {window_height})")

        return self.describe_website()

    def _get_website_main_content(self) -> str:
        texts = get_all_text_elements(self.driver)
        pretty_texts = [prettify_text(text) for text in texts]
        if not pretty_texts:
            return ""

        description = (
            "Current window displays the following contents, try scrolling up or down"
            " to view more: "
        )
        description += json.dumps(pretty_texts)

        return description

    def _get_interactable_elements(self) -> str:
        # Extract interactable components (buttons and links)
        interactable_elements = self.driver.find_elements(
            By.XPATH,
            "//button | //div[@role='button'] | //a | //input[@type='checkbox']",
        )

        interactable_texts = []
        for element in interactable_elements:
            button_text = find_parent_element_text(element)
            button_text = prettify_text(button_text, 50)
            if (
                button_text
                and button_text not in interactable_texts
                and element.is_displayed()
                and element.is_enabled()
            ):
                interactable_texts.append(button_text)

        # Split up the links and the buttons
        buttons_text = []
        links_text = []
        for text in interactable_texts:
            if validators.url(text):
                links_text.append(text)
            else:
                buttons_text.append(text)
        interactable_output = ""
        if links_text:
            interactable_output += f"Goto these links: {json.dumps(links_text)}\n"
        if buttons_text:
            interactable_output += f"Click on these buttons: {json.dumps(buttons_text)}"
        return interactable_output


class GoogleSearchInput(BaseModel):
    """Google search input model."""

    query: str = Field(..., description="search query")


class DescribeWebsiteInput(BaseModel):
    """Describe website input model."""

    url: str = Field(
        ...,
        description="full URL starting with http or https",
        example="https://www.google.com/",
    )


class ClickButtonInput(BaseModel):
    """Click button input model."""

    button_text: str = Field(
        ...,
        description="text of the button/link you want to click",
        example="Contact Us",
    )


class FindFormInput(BaseModel):
    """Find form input input model."""

    url: Optional[str] = Field(
        default=None,
        description="the current website url",
        example="https://www.google.com/",
    )


class FillOutFormInput(BaseModel):
    """Fill out form input model."""

    form_input: Optional[str] = Field(
        default=None,
        description="json formatted string with the input fields and their values",
        example='{"email": "foo@bar.com","name": "foo bar"}',
    )


class ScrollInput(BaseModel):
    """Scroll window."""

    direction: str = Field(
        default="down", description="direction to scroll, either 'up' or 'down'"
    )
