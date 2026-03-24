FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app
COPY core ./core
COPY src ./src
COPY README.md ./README.md
COPY config.yaml ./config.yaml
COPY streamlit_app.py ./streamlit_app.py

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]