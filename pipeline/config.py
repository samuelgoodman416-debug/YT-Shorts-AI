"""Loads pipeline settings from config.yaml."""

from pathlib import Path

import yaml

CONFIG_PATH = Path("config.yaml")


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
