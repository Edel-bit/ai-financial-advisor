FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Run as a non-root user (created before the model download so the cache belongs to it)
RUN useradd --create-home app && chown app /app
USER app

# Bake the embedding model into the image so startup doesn't download it
RUN python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2 as E; E()(['warm up'])"

COPY --chown=app src/ src/
COPY --chown=app .streamlit/ .streamlit/
COPY --chown=app --chmod=755 start.sh .

EXPOSE 8501
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"
CMD ["./start.sh"]
