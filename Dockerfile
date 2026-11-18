FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev && useradd --uid 10001 --create-home drama && mkdir -p /data/assets && chown -R drama:drama /data
ENV PATH="/app/.venv/bin:$PATH"
USER drama
CMD ["uvicorn", "drama_bot.app:app", "--host", "0.0.0.0", "--port", "8000"]
