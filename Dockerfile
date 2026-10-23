FROM python:3.14-slim AS base

ENV PATH="/opt/venv/bin:${PATH}" \
    PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/home/app/.cache/huggingface

WORKDIR /workspace/net-tools-app

FROM base AS build

COPY --from=ghcr.io/astral-sh/uv:0.12.1 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY --from=netops /pyproject.toml /README.md /workspace/net-ops-kb-rag/
COPY --from=netops /src /workspace/net-ops-kb-rag/src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

RUN python -c 'import importlib.metadata as metadata; import torch; installed = {dist.metadata["Name"].lower() for dist in metadata.distributions()}; forbidden = {name for name in installed if name.startswith(("nvidia-", "cuda-")) or name == "triton"}; assert torch.version.cuda is None, f"Expected CPU-only PyTorch, got CUDA {torch.version.cuda}"; assert not forbidden, f"Unexpected GPU dependencies: {sorted(forbidden)}"'

FROM base AS runtime

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --create-home app \
    && mkdir -p /workspace/net-ops-kb-rag/storage/chroma \
        /home/app/.cache/huggingface \
    && chown -R app:app /workspace/net-ops-kb-rag /home/app/.cache

COPY --from=build --chown=app:app /opt/venv /opt/venv

VOLUME ["/workspace/net-ops-kb-rag/storage/chroma", "/home/app/.cache/huggingface"]

USER app:app

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn net_tools_app.main:app --host 0.0.0.0 --port \"$PORT\""]
