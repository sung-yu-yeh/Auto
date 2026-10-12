
import pytest

from func.browser import create_browser
from func.config_loader import load_config, load_login_data
from func.logger import get_logger


@pytest.fixture(scope="session")
def config():
    return load_config()


@pytest.fixture(scope="session")
def credentials():
    return load_login_data()


@pytest.fixture(scope="session")
def logger():
    return get_logger("ui_automation")


@pytest.fixture
def driver(config, logger):
    browser = create_browser(
        config.get("browser", "edge")
    )
    browser.set_window_size(1440, 900)

    logger.info("Browser started")

    yield browser

    logger.info("Closing browser")
    browser.quit()
