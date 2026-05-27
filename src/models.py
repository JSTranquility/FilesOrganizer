from dataclasses import dataclass
from pathlib import Path


@dataclass
class PlannedMove:
    source: Path
    destination: Path
    category: str
