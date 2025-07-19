from __future__ import annotations

import csv
import json
from pathlib import Path
from collections import Counter

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import ValidationError

from app import __version__
from app.controls import canonical_control_set, map_controls_for_finding
from app.manifest import write_manifest
from app.models import Finding, GenerationResult, Metadata


class GenerationError(Exception):
    pass


def _load_metadata(input_dir: Path) -> Metadata:
    metadata_path = input_dir / "metadata.json"
    if not metadata_path.exists():
        raise GenerationError(f"Missing required metadata file: {metadata_path}")

    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        return Metadata.model_validate(payload)
    except json.JSONDecodeError as exc:
        raise GenerationError(f"Invalid JSON in metadata file: {metadata_path}") from exc
    except ValidationError as exc:
        raise GenerationError(f"Metadata validation failed: {exc}") from exc


def _pick(row: dict[str, str], *keys: str) -> str | None:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return None


def _load_findings(input_dir: Path) -> list[Finding]:
    findings_path = input_dir / "findings.csv"
    if not findings_path.exists():
        raise GenerationError(f"Missing required findings file: {findings_path}")

    findings: list[Finding] = []
    with findings_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise GenerationError("Findings CSV has no header row")

        for index, row in enumerate(reader, start=1):
            finding_id = _pick(row, "finding_id", "id", "key") or f"F-{index:04d}"
            title = _pick(row, "title", "name", "finding") or "Untitled finding"
            severity = _pick(row, "severity", "risk", "priority") or "medium"
            status = _pick(row, "status", "state") or "open"
            description = _pick(row, "description", "details")
            source = _pick(row, "source", "scanner")

            try:
                findings.append(
                    Finding(
                        finding_id=finding_id,
                        title=title,
                        severity=severity,
                        status=status,
                        description=description,
                        source=source,
                        raw={k: v for k, v in row.items() if k},
                    )
                )
            except ValidationError as exc:
                raise GenerationError(f"Invalid finding at row {index}: {exc}") from exc

    return findings


def _collect_evidence_paths(input_dir: Path) -> list[str]:
    evidence_dir = input_dir / "evidence"
    if not evidence_dir.exists():
        return []

    files = [p for p in evidence_dir.rglob("*") if p.is_file()]
    return [str(path.relative_to(input_dir)).replace("\\", "/") for path in sorted(files)]


def _apply_control_mapping(findings: list[Finding], control_set: str) -> dict[str, int]:
    summary = Counter()
    for finding in findings:
        mapped_controls = map_controls_for_finding(finding, control_set)
        finding.mapped_controls = mapped_controls
        summary.update(mapped_controls)
    return dict(summary)


def _render_html_report(
    *,
    output_dir: Path,
    metadata: Metadata,
    findings: list[Finding],
    evidence_files: list[str],
    control_summary: dict[str, int],
) -> Path:
    templates_dir = Path(__file__).parent / "templates"
    environment = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = environment.get_template("report.html.j2")

    html = template.render(
        metadata=metadata.model_dump(mode="json"),
        findings=[item.model_dump(mode="json") for item in findings],
        evidence_files=evidence_files,
        control_summary=control_summary,
    )

    output_path = output_dir / "evidence-pack.html"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def generate_evidence_pack(*, input_dir: Path, output_dir: Path) -> GenerationResult:
    if not input_dir.exists() or not input_dir.is_dir():
        raise GenerationError(f"Input directory does not exist: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    metadata = _load_metadata(input_dir)
    metadata.control_set = canonical_control_set(metadata.control_set)
    findings = _load_findings(input_dir)
    control_summary = _apply_control_mapping(findings, metadata.control_set)
    evidence_files = _collect_evidence_paths(input_dir)

    normalized_output_path = output_dir / "findings-normalised.json"
    normalized_output_path.write_text(
        json.dumps([item.model_dump(mode="json") for item in findings], indent=2),
        encoding="utf-8",
    )

    html_output_path = _render_html_report(
        output_dir=output_dir,
        metadata=metadata,
        findings=findings,
        evidence_files=evidence_files,
        control_summary=control_summary,
    )

    manifest_path = write_manifest(
        input_dir=input_dir,
        output_dir=output_dir,
        metadata=metadata.model_dump(mode="json"),
        tool_version=__version__,
    )

    return GenerationResult(
        findings_count=len(findings),
        evidence_count=len(evidence_files),
        output_files=[
            str(html_output_path),
            str(normalized_output_path),
            str(manifest_path),
        ],
    )
