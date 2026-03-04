import json
from pathlib import Path
from datetime import datetime


LEDGER_PATH = Path(".refinery/extraction_ledger.jsonl")


def log_entry(entry: dict) -> None:
    entry["timestamp"] = datetime.utcnow().isoformat()

    with LEDGER_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")
