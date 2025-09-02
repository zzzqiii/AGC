"""Initialization functions for Mol Research Agent."""

import logging
import os

# 设置API密钥

os.environ["OPENAI_API_KEY"] = "YOUR API KEY"
os.environ["OPENAI_API_BASE"] = "YOUR API BASE"

loglevel = os.getenv("GOOGLE_GENAI_FOMC_AGENT_LOG_LEVEL", "INFO")
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError(f"Invalid log level: {loglevel}")
logger = logging.getLogger(__package__)
logger.setLevel(numeric_level)

MODEL = os.getenv("GOOGLE_GENAI_MODEL")


# Import and expose the root_agent
# from .agent import root_agent