from __future__ import annotations

import shutil
import tempfile
from fastapi import FastAPI
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from pathlib import Path

from app import __version__
from app.controls import supported_control_sets
from app.generator import GenerationError, generate_evidence_pack

app = FastAPI(title="evidence-pack-generator", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "evidence-pack-generator", "version": __version__}


class GeneratePathRequest(BaseModel):
    input_dir: str
    output_dir: str


@app.get("/control-sets")
def control_sets() -> dict[str, list[str]]:
    return {"supported_control_sets": supported_control_sets()}


@app.post("/generate/path")
def generate_from_paths(payload: GeneratePathRequest) -> dict[str, object]:
    try:
        result = generate_evidence_pack(
            input_dir=Path(payload.input_dir),
            output_dir=Path(payload.output_dir),
        )
    except GenerationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "ok",
        "findings_count": result.findings_count,
        "evidence_count": result.evidence_count,
        "output_files": result.output_files,
    }


@app.post("/generate/upload")
async def generate_from_upload(
    metadata_file: UploadFile = File(...),
    findings_file: UploadFile = File(...),
    evidence_files: list[UploadFile] = File(default=[]),
    output_dir: str = Form(default="/tmp/evidence-pack-output"),
) -> dict[str, object]:
    temp_input = Path(tempfile.mkdtemp(prefix="evidence-pack-input-"))
    evidence_dir = temp_input / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    try:
        (temp_input / "metadata.json").write_bytes(await metadata_file.read())
        (temp_input / "findings.csv").write_bytes(await findings_file.read())

        for evidence in evidence_files:
            safe_name = Path(evidence.filename or "evidence.bin").name
            (evidence_dir / safe_name).write_bytes(await evidence.read())

        resolved_output_dir = Path(output_dir)
        result = generate_evidence_pack(input_dir=temp_input, output_dir=resolved_output_dir)
        return {
            "status": "ok",
            "findings_count": result.findings_count,
            "evidence_count": result.evidence_count,
            "output_files": result.output_files,
            "output_dir": str(resolved_output_dir),
        }
    except GenerationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        shutil.rmtree(temp_input, ignore_errors=True)
