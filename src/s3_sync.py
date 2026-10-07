"""Keep your documents and built database in an S3 bucket.

Why: a cloud server's disk can be wiped when it's replaced or redeployed. S3 is
the permanent copy. You build the database on your laptop, push it to S3, and
the server pulls it down when it starts.

    python src/s3_sync.py push      # laptop -> S3   (data/raw + chroma_db)
    python src/s3_sync.py pull      # S3 -> server   (runs automatically in Docker)

Needs S3_BUCKET in .env and AWS credentials (`aws configure` on your laptop;
an IAM role on the server, so no keys are stored there).
"""
import sys
from pathlib import Path

from config import CHROMA_DIR, DATA_DIR, PROJECT_ROOT, S3_BUCKET, S3_PREFIX

FOLDERS = {"data/raw": DATA_DIR, "chroma_db": CHROMA_DIR}


def _s3():
    import boto3

    if not S3_BUCKET:
        sys.exit("Set S3_BUCKET in your .env file first.")
    return boto3.client("s3")


def upload_file(local: Path, key: str):
    _s3().upload_file(str(local), S3_BUCKET, f"{S3_PREFIX}/{key}")


def push():
    s3 = _s3()
    for remote, local in FOLDERS.items():
        files = [p for p in Path(local).rglob("*") if p.is_file()]
        print(f"Uploading {len(files)} files from {local} ...")
        for p in files:
            key = f"{S3_PREFIX}/{remote}/{p.relative_to(local).as_posix()}"
            s3.upload_file(str(p), S3_BUCKET, key)
    print(f"Done: s3://{S3_BUCKET}/{S3_PREFIX}/")


def pull():
    s3 = _s3()
    paginator = s3.get_paginator("list_objects_v2")
    count = 0
    for remote, local in FOLDERS.items():
        prefix = f"{S3_PREFIX}/{remote}/"
        for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
            for obj in page.get("Contents", []):
                dest = Path(local) / obj["Key"][len(prefix):]
                dest.parent.mkdir(parents=True, exist_ok=True)
                s3.download_file(S3_BUCKET, obj["Key"], str(dest))
                count += 1
    print(f"Downloaded {count} files from s3://{S3_BUCKET}/{S3_PREFIX}/ into {PROJECT_ROOT}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "push":
        push()
    elif cmd == "pull":
        pull()
    else:
        sys.exit(__doc__)
