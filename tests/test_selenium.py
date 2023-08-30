"""Integration test for Selenium API Wrapper."""

from chromegpt.tools.driver import SeleniumWrapper, execute_with_driver


@execute_with_driver
def test_describe_website(client: SeleniumWrapper) -> None:
    """Test that SeleniumWrapper returns correct website"""
    output = None
    output = client.describe_website("https://example.com")
    assert output is not None and "this domain is for use in illu" in output


@execute_with_driver
def test_click(client: SeleniumWrapper) -> None:
    """Test that SeleniumWrapper click works"""

    output = None
    client.describe_website("https://example.com")
    output = client.click_button_by_text('link with title "More information..."')
    assert (
        output is not None
        and "Clicked interactable element and the website changed" in output
    )


@execute_with_driver
def test_google_input(client: SeleniumWrapper) -> None:
    """Test that SeleniumWrapper can find input form"""
    output = None
    output = client.find_form_inputs("https://google.com")
    assert output is not None and "q" in output


@execute_with_driver
def test_google_fill(client: SeleniumWrapper) -> None:
    """Test that SeleniumWrapper can fill input form"""
    output = None
    client.find_form_inputs("https://google.com")
    output = client.fill_out_form(q="hello world")

    assert output is not None and "website changed after filling out form" in output


@execute_with_driver
def test_google_search(client: SeleniumWrapper) -> None:
    """Test google search functionality"""
    output = None
    output = client.google_search("hello world")
    assert output is not None and "hello" in output
    assert output is not None and "Which url would you like to goto" in output
