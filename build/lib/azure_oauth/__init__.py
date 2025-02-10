# azure_oauth/__init__.py

"""_summary_
"""

import json
from typing import List, Dict
from pathlib import Path

from .arg_example import parser
from .main import main

with open(Path(__file__).parent / "service_config.json", encoding="utf-8") as file:
    service_config: Dict[str, Dict[str, str]] = json.load(file)

__all__: List[str] = [
    "service_config",
    "parser",
    "main"
]
