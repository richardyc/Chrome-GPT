"""Utils for chromegpt tools."""

import re
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver

### Main Content Extraction ###
def is_complete_sentence(text: str) -> bool:
    return re.search(r'[.!?]\s*$', text) is not None

def get_all_text_elements(driver: WebDriver) -> List[str]:
    xpath = "//*[not(self::script or self::style or self::noscript)][string-length(normalize-space(text())) > 0]"
    elements = driver.find_elements(By.XPATH, xpath)
    texts = [element.text.strip() for element in elements if element.text.strip() and is_complete_sentence(element.text.strip())]
    return texts

def find_interactable_elements(driver: WebDriver) -> List[str]:
    # Extract interactable components (buttons and links)
    buttons = driver.find_elements(By.XPATH, "//button")
    links = driver.find_elements(By.XPATH, "//a")

    interactable_elements = buttons + links

    interactable_output = []
    for element in interactable_elements:
        element_text = element.text.strip()
        if element_text and element_text not in interactable_output:
            element_text = prettify_text(element_text)
            interactable_output.append(element_text)
    return interactable_output

def prettify_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

