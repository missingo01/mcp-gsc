FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml README.md ./

RUN uv sync --no-cache --no-install-project

COPY gsc_server.py .
COPY render_server.py .

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "--no-sync", "python", "render_server.py"]