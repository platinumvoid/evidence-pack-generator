from __future__ import annotations

from dataclasses import dataclass

from app.models import Finding


@dataclass(frozen=True)
class MappingRule:
    keywords: tuple[str, ...]
    controls: tuple[str, ...]


CONTROL_MAPPINGS: dict[str, tuple[MappingRule, ...]] = {
    "DORA": (
        MappingRule(("patch", "dependency", "outdated", "cve"), ("DORA-ICT-RM-01", "DORA-ICT-RM-03")),
        MappingRule(("vulnerability", "scanner", "nessus"), ("DORA-TEST-01",)),
        MappingRule(("header", "tls", "cipher", "encryption"), ("DORA-SEC-02",)),
    ),
    "PCI DSS": (
        MappingRule(("tls", "cipher", "encryption", "certificate"), ("PCI-4.2", "PCI-4.1")),
        MappingRule(("vulnerability", "nessus", "scan"), ("PCI-11.3.1",)),
        MappingRule(("dependency", "package", "outdated", "cve"), ("PCI-6.3.3",)),
    ),
    "ISO 27001": (
        MappingRule(("vulnerability", "scan", "scanner"), ("ISO-A.8.8",)),
        MappingRule(("patch", "dependency", "outdated", "cve"), ("ISO-A.8.8", "ISO-A.8.9")),
        MappingRule(("header", "tls", "cipher", "encryption"), ("ISO-A.8.24", "ISO-A.8.26")),
    ),
}


CONTROL_SET_ALIASES = {
    "PCI": "PCI DSS",
    "PCIDSS": "PCI DSS",
    "DORA": "DORA",
    "ISO": "ISO 27001",
    "ISO27001": "ISO 27001",
    "ISO 27001": "ISO 27001",
}


DEFAULT_CONTROL_SET = "ISO 27001"


def canonical_control_set(control_set: str | None) -> str:
    if not control_set:
        return DEFAULT_CONTROL_SET

    text = " ".join(control_set.upper().split())
    return CONTROL_SET_ALIASES.get(text, control_set)


def supported_control_sets() -> list[str]:
    return sorted(CONTROL_MAPPINGS.keys())


def map_controls_for_finding(finding: Finding, control_set: str) -> list[str]:
    selected = canonical_control_set(control_set)
    rules = CONTROL_MAPPINGS.get(selected, ())

    search_parts: list[str] = [finding.title]
    if finding.description:
        search_parts.append(finding.description)
    if finding.source:
        search_parts.append(finding.source)

    for key, value in finding.raw.items():
        search_parts.append(f"{key} {value}")

    search_text = " ".join(search_parts).lower()

    mapped: set[str] = set()
    for rule in rules:
        if any(keyword in search_text for keyword in rule.keywords):
            mapped.update(rule.controls)

    if not mapped:
        mapped.add("UNMAPPED")

    return sorted(mapped)
