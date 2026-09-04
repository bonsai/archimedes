from .models import Asset, Relation, Task
from .analyzer import clusters


def advise(assets: list[Asset], relations: list[Relation]) -> list[Task]:
    linked = {x for r in relations for x in (r.source, r.target)}
    tasks: list[Task] = []
    isolated = [a for a in assets if a.id not in linked]
    if isolated:
        tasks.append(Task(
            id="discover-isolated-assets", objective="Investigate isolated assets and add useful metadata or relations",
            evidence=[f"{len(isolated)} assets have no inferred relation"], affected_assets=[a.id for a in isolated[:50]],
            priority=min(1.0, 0.4 + len(isolated) / max(1, len(assets))), executor="archimedes-search",
            acceptance=["Each relevant isolated asset has metadata", "Useful relations are persisted"]
        ))
    group_count = len(clusters(assets))
    if group_count > 10:
        tasks.append(Task(
            id="ontology-normalization", objective="Review fragmented asset vocabulary and normalize ontology terms",
            evidence=[f"{group_count} coarse clusters detected"], priority=0.7, executor="ontology-agent",
            acceptance=["Canonical asset kinds are defined", "Aliases map to canonical terms"]
        ))
    tasks.append(Task(
        id="persist-observation", objective="Persist the current observation so future scans can measure change",
        evidence=[f"{len(assets)} assets", f"{len(relations)} relations"], priority=0.8, executor="gh-aw",
        acceptance=["Observation is stored", "Previous observation remains queryable", "Delta can be computed"]
    ))
    return tasks
