from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def list_files_with_hashes(base_dir: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    if not base_dir.exists():
        return entries

    for file_path in sorted(p for p in base_dir.rglob("*") if p.is_file()):
        entries.append(
            {
                "path": str(file_path.relative_to(base_dir)).replace("\\", "/"),
                "sha256": sha256_file(file_path),
                "size_bytes": file_path.stat().st_size,
            }
        )
    return entries


def build_manifest(*, input_dir: Path, output_dir: Path, metadata: dict[str, object], tool_version: str) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "tool": "evidence-pack-generator",
        "tool_version": tool_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata,
        "input_files": list_files_with_hashes(input_dir),
        "output_files": list_files_with_hashes(output_dir),
    }


def write_manifest(*, input_dir: Path, output_dir: Path, metadata: dict[str, object], tool_version: str) -> Path:
    manifest = build_manifest(
        input_dir=input_dir,
        output_dir=output_dir,
        metadata=metadata,
        tool_version=tool_version,
    )
    output_path = output_dir / "manifest.json"
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output_path
