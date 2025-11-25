# Minimal Dockerfile for KGEB
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Include dev deps optionally
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then pip install --no-cache-dir -e .[dev]; else pip install --no-cache-dir -e .; fi

ENTRYPOINT ["kgeb"]
CMD ["run", "--documents", "documents.txt", "--entities-schema", "entities.json", "--relations-schema", "relations.json"]
