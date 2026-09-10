# Export config object, functions

from app.config.settings import get_app_config, get_settings
from app.config.models import AppConfig

__all__ = ["get_app_config", "get_settings", "AppConfig"]

config = get_app_config()