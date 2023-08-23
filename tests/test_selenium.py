"""Integration test for Selenium API Wrapper."""

# import pytest

from chromegpt.tools.selenium import SeleniumWrapper


# @pytest.fixture
# def client() -> SeleniumWrapper:
#     return SeleniumWrapper(headless=True)


def test_describe_website() -> None:
    """Test that SeleniumWrapper returns correct website"""
    client = SeleniumWrapper(headless=True)
    output = None
    try:
        output = client.describe_website("https://example.com")
    finally:
        del client
    assert output is not None and "this domain is for use in illu" in output


def test_click() -> None:
    """Test that SeleniumWrapper click works"""
    client = SeleniumWrapper(headless=True)
    output = None
    try:
        client.describe_website("https://example.com")
        output = client.click_button_by_text('link with title "More information..."')
    finally:
        del client
    assert output is not None and "Clicked interactable element and the website changed" in output


def test_google_input() -> None:
    """Test that SeleniumWrapper can find input form"""
    client = SeleniumWrapper(headless=True)
    output = None
    try:
        output = client.find_form_inputs("https://google.com")
    finally:
        del client
    assert output is not None and "q" in output


def test_google_fill() -> None:
    """Test that SeleniumWrapper can fill input form"""
    client = SeleniumWrapper(headless=True)
    output = None
    try:
        client.find_form_inputs("https://google.com")
        output = client.fill_out_form(q="hello world")
    finally:
        del client
    assert output is not None and "website changed after filling out form" in output


def test_google_search() -> None:
    """Test google search functionality"""
    client = SeleniumWrapper(headless=True)
    output = None
    try:
        output = client.google_search("hello world")
    finally:
        del client
    assert output is not None and "hello" in output
    assert output is not None and "Which url would you like to goto" in output
