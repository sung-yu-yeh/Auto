
from selenium import webdriver
from selenium.webdriver.edge.options import Options


def create_browser(browser_name: str = "edge"):
    """Create a Microsoft Edge WebDriver."""
    if browser_name.lower() != "edge":
        raise ValueError(f"Unsupported browser: {browser_name}")

    options = Options()
    driver = webdriver.Edge(options=options)
    driver.set_window_size(1440, 900)
    return driver
