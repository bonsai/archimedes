from __future__ import annotations
import argparse, json
from pathlib import Path
from .scanner import scan_local, scan_github, write_jsonl
from .models import Asset, Relation
from .analyzer import infer_relations, summarize
from .advisor import advise

def load_assets(path: str) -> list[Asset]:
    return [Asset(**json.loads(line)) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]

def main() -> None:
    p = argparse.ArgumentParser(prog="archimedes")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scan"); s.add_argument("--path", default="."); s.add_argument("--owner"); s.add_argument("--out", default="data/assets.jsonl")
    a = sub.add_parser("analyze"); a.add_argument("assets")
    v = sub.add_parser("advise"); v.add_argument("assets")
    t = sub.add_parser("task"); t.add_argument("assets")
    args = p.parse_args()
    if args.command == "scan":
        assets = scan_github(args.owner) if args.owner else scan_local(args.path)
        write_jsonl(assets, args.out); print(json.dumps({"assets": len(assets), "out": args.out}, ensure_ascii=False))
        return
    assets = load_assets(args.assets)
    relations = infer_relations(assets)
    if args.command == "analyze": print(json.dumps(summarize(assets, relations), ensure_ascii=False, indent=2))
    elif args.command in {"advise", "task"}:
        tasks = advise(assets, relations)
        print("\n".join(json.dumps(x.to_dict(), ensure_ascii=False) for x in tasks))

if __name__ == "__main__": main()
