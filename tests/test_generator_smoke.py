from pathlib import Path

from app.generator import generate_evidence_pack


def test_generate_evidence_pack_smoke(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    evidence_dir = input_dir / "evidence"
    output_dir = tmp_path / "output"

    evidence_dir.mkdir(parents=True)
    (input_dir / "metadata.json").write_text(
        '{"project":"Test Project","owner":"QA","control_set":"ISO 27001"}',
        encoding="utf-8",
    )
    (input_dir / "findings.csv").write_text(
        "id,title,severity,status\nF-1,Sample finding,high,open\n",
        encoding="utf-8",
    )
    (evidence_dir / "nessus-summary.txt").write_text("sample", encoding="utf-8")

    result = generate_evidence_pack(input_dir=input_dir, output_dir=output_dir)

    assert result.findings_count == 1
    assert (output_dir / "evidence-pack.html").exists()
    assert (output_dir / "findings-normalised.json").exists()
    assert (output_dir / "manifest.json").exists()
