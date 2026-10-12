
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from func.config_loader import load_test_config, load_locators
from func.logger import get_logger


logger = get_logger(__name__)

LOCATOR_TYPES = {
    "id": By.ID,
    "name": By.NAME,
    "css selector": By.CSS_SELECTOR,
    "xpath": By.XPATH,
    "class name": By.CLASS_NAME,
    "tag name": By.TAG_NAME,
}


def find_element(driver, locator_config: dict, timeout: int = 10):
    """Find an element using Locator.json configuration."""
    by_name = locator_config["by"].lower()
    value = locator_config["value"]

    if by_name not in LOCATOR_TYPES:
        raise ValueError(f"Unsupported locator type: {by_name}")

    locator = (LOCATOR_TYPES[by_name], value)

    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )


def login(driver, config: dict, credentials: dict) -> str:
    """Submit the login form and return the resulting browser URL."""
    locator_config = load_locators()
    timeout = config.get("timeout", 10)

    logger.info("Opening URL: %s", config["url"])
    driver.get(config["url"])

    password_element = find_element(
        driver,
        locator_config["login"]["enter_password"],
        timeout,
    )
    password_element.clear()
    password_element.send_keys(credentials["password"])

    button_locator = locator_config["login"]["login_button"]
    button_by = button_locator["by"].lower()
    if button_by not in LOCATOR_TYPES:
        raise ValueError(f"Unsupported locator type: {button_by}")

    button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(
            (LOCATOR_TYPES[button_by], button_locator["value"])
        )
    )
    button.click()
    logger.info("Login button clicked")

    return driver.current_url


def run_login():
    """Read configuration, open URL, enter password and login."""
    config = load_test_config()
    from func.browser import create_browser

    driver = create_browser(config.get("browser", "edge"))

    try:
        result_url = login(driver, config, {"password": config["password"]})
        assert result_url, "Browser URL is empty"
        logger.info("Login action completed")

    except Exception:
        logger.exception("Login automation failed")
        raise

    finally:
        driver.quit()


if __name__ == "__main__":
    run_login()
