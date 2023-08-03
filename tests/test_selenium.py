"""Integration test for Selenium API Wrapper."""

import pytest

from chromegpt.tools.selenium import SeleniumWrapper


@pytest.fixture
def client() -> SeleniumWrapper:
    return SeleniumWrapper(headless=True)


def test_describe_website(client: SeleniumWrapper) -> None:
    """Test that SeleniumWrapper returns correct website"""

    output = client.describe_website("https://example.com")
    assert "this domain is for use in illu" in output


def test_click(client: SeleniumWrapper) -> None:
    """Test that SeleniumWrapper click works"""

    client.describe_website("https://example.com")
    output = client.click_button_by_text('link with title "More information..."')
    assert "Clicked interactable element and the website changed" in output


def test_google_input(client: SeleniumWrapper) -> None:
    """Test that SeleniumWrapper can find input form"""

    output = client.find_form_inputs("https://google.com")
    assert "q" in output


def test_google_fill(client: SeleniumWrapper) -> None:
    """Test that SeleniumWrapper can fill input form"""

    client.find_form_inputs("https://google.com")
    output = client.fill_out_form(q="hello world")
    assert "website changed after filling out form" in output


def test_google_search(client: SeleniumWrapper) -> None:
    """Test google search functionality"""
    res = client.google_search("hello world")
    assert "hello" in res
    assert "Which url would you like to goto" in res
