#!/bin/sh
# Container startup: pull the knowledge base from S3 (if configured), then run the app.
set -e
if [ -n "$S3_BUCKET" ]; then
  python src/s3_sync.py pull
fi
exec streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
