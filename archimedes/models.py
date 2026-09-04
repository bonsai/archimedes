from dataclasses import asdict, dataclass, field
from typing import Any

LIFECYCLES = {"permanent", "reusable", "experimental", "ephemeral", "archived"}

@dataclass
class Asset:
    id: str
    kind: str
    name: str
    path: str | None = None
    repository: str | None = None
    language: str | None = None
    lifecycle: str = "reusable"
    terms: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.lifecycle not in LIFECYCLES:
            raise ValueError(f"unknown lifecycle: {self.lifecycle}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class Relation:
    source: str
    predicate: str
    target: str
    score: float = 1.0
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class Task:
    id: str
    objective: str
    evidence: list[str] = field(default_factory=list)
    affected_assets: list[str] = field(default_factory=list)
    priority: float = 0.5
    executor: str = "specialist-agent"
    acceptance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
