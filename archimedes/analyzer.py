from collections import Counter, defaultdict
from itertools import combinations
from .models import Asset, Relation


def infer_relations(assets: list[Asset], threshold: int = 2) -> list[Relation]:
    out: list[Relation] = []
    for a, b in combinations(assets, 2):
        if a.repository and b.repository and a.repository == b.repository and a.kind == "repository" and b.kind == "repository":
            continue
        overlap = sorted(set(a.terms) & set(b.terms))
        if len(overlap) >= threshold:
            out.append(Relation(a.id, "related_to", b.id, min(1.0, len(overlap) / 10), overlap[:10]))
        if a.repository and b.repository and a.repository == b.repository and a.kind != b.kind:
            if a.kind in {"config", "documentation", "workflow"} or b.kind in {"config", "documentation", "workflow"}:
                out.append(Relation(a.id, "belongs_to_context", b.id, 1.0, [a.repository]))
    return out


def clusters(assets: list[Asset]) -> dict[str, list[str]]:
    groups = defaultdict(list)
    for a in assets:
        groups[f"{a.kind}:{a.language or 'none'}"].append(a.id)
    return dict(groups)


def summarize(assets: list[Asset], relations: list[Relation]) -> dict:
    return {
        "assets": len(assets),
        "relations": len(relations),
        "kinds": dict(Counter(a.kind for a in assets)),
        "languages": dict(Counter(a.language for a in assets if a.language)),
        "clusters": len(clusters(assets)),
        "isolated": len(set(a.id for a in assets) - {r.source for r in relations} - {r.target for r in relations}),
    }
