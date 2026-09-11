# Get logger object

import logging

# Get logger
def get_logger(name: str) -> logging.Logger:
    """Wrapper for codebase"""
    return logging.getLogger(name)