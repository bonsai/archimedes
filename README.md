# Archimedes

**Repository Architecture Agent for bonsai**

Archimedes observes the repository ecosystem, turns code and GitHub metadata into structured Assets, infers Relations, detects clusters and gaps, and produces the next development Tasks.

> Filesystem is storage. Metadata is memory. Search is access. Ontology is meaning. BQML is discovery. Archimedes is direction.

## Role boundary

- **Archimedes** = architect / observer / planner. It decides *what should happen next*.
- **gh-aw** = execution tool / workflow substrate. It performs GitHub-side actions.
- **Other agents** = specialists that implement bounded Tasks.

Archimedes must not become a giant implementation agent. It creates small, evidence-backed Tasks and delegates execution.

## Loop

```text
SCAN → STRUCTURE → RELATE → CLUSTER → FIND GAPS → ADVISE → TASK → EXECUTE → RESCAN
```

## MVP

```bash
python -m archimedes.cli scan --path .
python -m archimedes.cli analyze data/assets.jsonl
python -m archimedes.cli advise data/assets.jsonl
python -m archimedes.cli task data/assets.jsonl
```

The scanner also supports a GitHub owner scan using the GitHub REST API.

## Architecture

```text
GitHub / local repos
        ↓
     Scanner
        ↓
      Asset
        ↓
 Relation / Cluster
        ↓
      Advisor
        ↓
       Task
        ↓
       gh-aw
        ↓
    repository changes
        ↓
      rescan
```

## Design principle

Directory layout is not the interface for an agent. Searchable metadata, relations, aliases, lifecycle state, and evidence are.
