from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

DATA_DIR = Path("data")
OUT_FILE = Path("checksums.sha256")


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_data_files() -> list[Path]:
    if not DATA_DIR.exists():
        return []
    files = sorted([p for p in DATA_DIR.rglob("*") if p.is_file()])
    return files


def write_checksums(paths: list[Path]) -> None:
    lines: list[str] = []
    for p in paths:
        digest = sha256_file(p)
        rel = p.as_posix()
        lines.append(f"{digest}  {rel}")
    OUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_checksums() -> dict[str, str]:
    if not OUT_FILE.exists():
        return {}
    rows: dict[str, str] = {}
    for line in OUT_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Format: <sha256><two spaces><path>
        parts = line.split()
        if len(parts) < 2:
            continue
        digest = parts[0]
        rel_path = parts[1]
        rows[rel_path] = digest
    return rows


def verify(paths: list[Path]) -> int:
    expected = read_checksums()
    if not expected:
        print("checksums.sha256 is missing. Generate with: python scripts/make_checksums.py")
        return 1

    mismatched: list[str] = []
    for p in paths:
        rel = p.as_posix()
        got = sha256_file(p)
        exp = expected.get(rel)
        if exp is None or exp != got:
            mismatched.append(rel)

    if mismatched:
        sample = mismatched[:5]
        print(f"Mismatched checksums for {len(mismatched)} files (example: {sample})")
        print("checksums.sha256 does not match current data files.")
        print("Re-generate with: python scripts/make_checksums.py")
        return 1

    print("checksums.sha256 matches current data files")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check",
        action="store_true",
        help="Verify checksums.sha256 instead of writing it",
    )
    args = ap.parse_args()

    paths = iter_data_files()
    if not paths:
        print("No data files found under ./data/")
        return 1

    if args.check:
        return verify(paths)

    write_checksums(paths)
    print(f"Wrote {OUT_FILE.as_posix()} with {len(paths)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
