# evidence-pack-generator

Generate audit-ready security evidence packs from structured findings, files, and screenshots.

A reproducible internal container for generating consistent audit and security evidence packs across SDLC, vulnerability management, penetration testing, and regulatory assurance workflows.

The first milestone is not perfect reporting. It is proving that the organisation can run the same container and get the same structured output every time.

## MVP Scope

Input layout:

```
input/
├── findings.csv
├── evidence/
│   ├── screenshot1.png
│   └── nessus-summary.txt
└── metadata.json
```

Output layout:

```
output/
├── evidence-pack.html
├── findings-normalised.json
└── manifest.json
```

## Local CLI Usage

```bash
python -m app.cli generate --input ./examples/basic --output ./output
```

## Docker Usage (Windows CMD/PowerShell style)

Build image:

```bash
docker build -t evidence-pack-generator .
```

Run generator:

```bash
docker run --rm \
  -v "%cd%/examples/basic:/input" \
  -v "%cd%/output:/output" \
  evidence-pack-generator generate \
  --input /input \
  --output /output
```

Run API server:

```bash
docker run --rm -p 8000:8000 evidence-pack-generator
```

The image uses an entrypoint launcher:

- `ENTRYPOINT ["/entrypoint.sh"]`
- `CMD ["api"]`

This allows both API default startup and explicit CLI mode (`generate`) in the same image.

Expected files:

- output/evidence-pack.html
- output/findings-normalised.json
- output/manifest.json

## Metadata Example

```json
{
  "project": "Payments API",
  "owner": "Security Engineering",
  "control_set": "DORA",
  "version": "0.1.0",
  "git_commit": "abc1234"
}
```

## Notes

- Findings CSV supports flexible column names and normalises into a consistent JSON schema.
- Manifest includes SHA-256 hashes for all input and output files.
- Simple control mapping is included for PCI DSS, DORA, and ISO 27001.
- PDF generation is intentionally deferred to a later milestone.

## API Endpoints (MVP)

- `GET /health`: service status
- `GET /control-sets`: supported control mapping sets
- `POST /generate/path`: generate from mounted input/output paths
- `POST /generate/upload`: upload `metadata.json`, `findings.csv`, and optional evidence files

## Docker Compose Usage

Run API service (default):

```bash
docker compose up --build
```

Run a one-off batch generation job:

```bash
docker compose --profile batch run --rm evidence-pack-generator
```

Container hardening highlights:

- Non-root runtime user in image
- Healthcheck on /health
- Read-only root filesystem and tmpfs /tmp in compose
- no-new-privileges security option
