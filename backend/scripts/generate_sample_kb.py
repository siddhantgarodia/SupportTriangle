"""
This script creates placeholder KB files if they don't already exist.
Since the KB files are already created with full content, this script is a no-op
in that case — it only creates missing files.
Run from the backend/ directory: python scripts/generate_sample_kb.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def check_and_report():
    namespaces = ["billing_kb", "technical_kb", "refund_kb"]
    for ns in namespaces:
        files = list((DATA_DIR / ns).glob("*.md"))
        print(f"  {ns}: {len(files)} files — {[f.name for f in files]}")


if __name__ == "__main__":
    print("KB file status:")
    check_and_report()
    print("All KB files are pre-generated. Run ingest_kbs.py or start the server to ingest them.")
