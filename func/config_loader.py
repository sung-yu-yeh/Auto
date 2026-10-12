
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_json(relative_path: str) -> dict:
    """Load a JSON file relative to the project root."""
    file_path = PROJECT_ROOT / relative_path

    if not file_path.is_file():
        raise FileNotFoundError(
            f"JSON file not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        result = json.load(file)

    if not isinstance(result, dict):
        raise ValueError(
            f"Expected a JSON object in {file_path}"
        )

    return result


def load_config() -> dict:
    return load_test_config()


def load_login_data() -> dict:
    config = load_test_config()
    return {"password": config["password"]}


def load_test_config() -> dict:
    return load_json("config_relate/test.json")


def load_locators() -> dict:
    return load_json("config_relate/Locator.json")
