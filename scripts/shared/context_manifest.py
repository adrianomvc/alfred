import re
from pathlib import Path

from shared.common import read_lines


PHASE_ALIASES = {
    "validate": "validation",
    "validation": "validation",
    "operation": "operations",
    "operations": "operations",
}


class ContextManifestError(ValueError):
    pass


def normalize(value):
    return str(value or "").strip().lower()


def normalize_phase(value):
    value = normalize(value)
    return PHASE_ALIASES.get(value, value)


def normalize_slug(value):
    return normalize(value).replace("_", "-").replace(" ", "-")


def parse_rules_index(root):
    index = Path(root) / "rules" / "rules-index.md"
    if not index.exists():
        raise ContextManifestError(f"Missing rules index: {index}")

    rows = []
    for line in read_lines(index):
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8:
            continue
        name, load, phase, lane, demand_type, agent, _, link_cell = cells
        link_match = re.search(r"\(([^)]+)\)", link_cell)
        if not link_match:
            continue
        rows.append(
            {
                "name": name.strip("`"),
                "load": load.strip("`"),
                "phase": phase.strip("`"),
                "lane": lane.strip("`"),
                "demand_type": demand_type.strip("`"),
                "agent": agent.strip("`"),
                "path": link_match.group(1),
            }
        )
    return rows


def find_one(rows, load, field, value):
    matches = [
        row for row in rows
        if row["load"] == load and normalize_slug(row[field]) == normalize_slug(value)
    ]
    if not matches:
        raise ContextManifestError(f"No {load} rule found for {field}={value}")
    return matches[0]["path"]


def find_sub_activity(rows, phase, sub_activity):
    wanted = normalize_slug(sub_activity)
    matches = [
        row for row in rows
        if row["load"] == "sub-activity"
        and normalize_phase(row["phase"]) == phase
        and (
            normalize_slug(row["name"].replace("sub-activity-", "")) == wanted
            or normalize_slug(Path(row["path"]).stem) == wanted
        )
    ]
    if not matches:
        raise ContextManifestError(f"No sub-activity found for phase={phase} sub_activity={sub_activity}")
    return matches[0]["path"]


def build_manifest(root, phase, lane, demand_type, agent, sub_activity=None, playbook=None):
    root = Path(root)
    phase = normalize_phase(phase)
    lane = normalize_slug(lane)
    demand_type = normalize_slug(demand_type)
    agent = normalize_slug(agent)
    rows = parse_rules_index(root)

    # Stable prefix first: keeps prompt caching effective when the host supports
    # it, and remains a plain JIT loading order everywhere else.
    ordered = [
        "core/principles.md",
        "rules/README.md",
        "rules/rules-index.md",
        find_one(rows, "always", "name", "common-overconfidence"),
        find_one(rows, "lifecycle", "name", "lifecycle"),
        find_one(rows, "demand-type", "demand_type", demand_type),
    ]
    # Playbook (JIT) loads next to its demand type when one applies to the demand.
    if playbook:
        ordered.append(find_one(rows, "playbook", "name", f"playbook-{normalize_slug(playbook)}"))
    ordered += [
        find_one(rows, "lane", "lane", lane),
        find_one(rows, "phase", "phase", phase),
        find_one(rows, "agent", "agent", agent),
    ]
    if sub_activity:
        ordered.append(find_sub_activity(rows, phase, sub_activity))

    seen = set()
    result = []
    for item in ordered:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
