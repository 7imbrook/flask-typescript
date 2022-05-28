from dataclasses import dataclass


@dataclass(frozen=True)
class SimpleID:
    id: int
