
from func.browser import create_browser
from func.config_loader import load_config, load_login_data
from func.logger import get_logger
from func.login import login


def test_login_success():
    config = load_config()
    credentials = load_login_data()
    logger = get_logger("ui_automation")
    driver = create_browser(config.get("browser", "edge"))

    logger.info("Test started: login success")

    try:
        result_url = login(driver, config, credentials)
        assert result_url, "Login submission left the browser URL empty"
        logger.info("Test passed: login success")
    finally:
        logger.info("Closing browser")
        driver.quit()
