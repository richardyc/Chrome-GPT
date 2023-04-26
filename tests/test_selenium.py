"""Integration test for Selenium API Wrapper."""
import pytest

from chromegpt.tools.selenium import SeleniumWrapper



@pytest.fixture
def client() -> SeleniumWrapper:
    return SeleniumWrapper(headless=True)


def test_describe_website(client: SeleniumWrapper) -> None:
    """Test that SeleniumWrapper returns correct website"""

    output = client.describe_website("https://example.com")
    assert "This domain is for use in illustrative examples in documents" in output


def test_click(client: SeleniumWrapper) -> None:
    """Test that SeleniumWrapper click works"""

    client.describe_website("https://example.com")
    output = client.click_button_by_text("More information...")
    assert "Clicked interactable element with text" in output
