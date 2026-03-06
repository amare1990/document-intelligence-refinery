# src/utils/ldu_loader.py

import json
from pathlib import Path
from typing import List

from src.models.ldu import LDU


def load_ldus(ldu_dir: Path) -> List[LDU]:

    ldus = []

    for file in ldu_dir.glob("*.json"):

        data = json.loads(file.read_text())

        for item in data:
            ldus.append(LDU(**item))

    return ldus
