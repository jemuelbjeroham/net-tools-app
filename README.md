# net-tools-app

FastAPI service exposing network-operations knowledge-base search through
`POST /api/v1/search`. The health endpoint is `GET /health`.

## Run with Docker

The image uses Python 3.14 and the committed `uv.lock`. Its build needs the
adjacent `net-ops-kb-rag` checkout because that package is a local editable
dependency in `pyproject.toml`.

From this directory, build for an Apple Silicon Mac:

```sh
docker buildx build \
  --build-context netops=../net-ops-kb-rag \
  --platform linux/arm64 \
  --tag net-tools-app:cpu-arm64-test \
  --load .
```

Build an AMD64 image (the build can run under BuildKit emulation on an ARM64
machine):

```sh
docker buildx build \
  --build-context netops=../net-ops-kb-rag \
  --platform linux/amd64 \
  --tag net-tools-app:cpu-amd64-test \
  --load .
```

Verify the AMD64 image's architecture:

```sh
docker image inspect net-tools-app:cpu-amd64-test --format '{{.Os}}/{{.Architecture}}'
```

To run the AMD64 image under emulation and check its health endpoint, Docker
Desktop (or another Docker installation with AMD64 emulation enabled) must be
available. The service downloads its embedding model on first startup, so it
needs outbound access to Hugging Face unless that cache is already populated.
The Chroma volume must contain the indexed knowledge base for searches to
return results.

```sh
docker run --rm \
  --platform linux/amd64 \
  --publish 8000:8000 \
  --volume net-tools-chroma:/workspace/net-ops-kb-rag/storage/chroma \
  --volume net-tools-huggingface:/home/app/.cache/huggingface \
  --name net-tools-app \
  net-tools-app:cpu-amd64-test
```

In another terminal:

```sh
curl --fail http://localhost:8000/health
```

The container listens on `0.0.0.0:8000` by default. Set `PORT` to change its
internal listening port and publish that same port. `NET_TOOLS_API_URL` is a
client-side setting for `lisa-api`; it is not read by this service.

## Runtime requirements

- No service credentials or `.env` file are required.
- The service downloads `Qwen/Qwen3-Embedding-0.6B` from Hugging Face during
  startup and needs outbound network access on a cold cache.
- ChromaDB writes to `../net-ops-kb-rag/storage/chroma`, relative to the
  container working directory. Mount a writable, populated Chroma data
  directory at `/workspace/net-ops-kb-rag/storage/chroma` to retain the
  knowledge base across container restarts.
- Linux ARM64 and AMD64 wheels are present for the locked native dependencies,
  including CPU-only PyTorch 2.13.0, ChromaDB 1.5.9, PyMuPDF 1.28.2,
  tokenizers 0.23.1, and ONNX Runtime 1.29.0. Linux PyTorch is pinned to the
  explicit PyTorch CPU package index in `pyproject.toml`; the Docker build
  verifies that no CUDA or Triton distributions are installed.

## lisa-api integration

Run both containers on the same Docker network and give this container the
network alias `net-tools-app`. Keep `NET_TOOLS_API_URL=http://net-tools-app:8000`
in `lisa-api`; no host port publishing is needed for container-to-container
traffic. If `PORT` is changed from `8000`, update `NET_TOOLS_API_URL` to match.
Mount the populated Chroma data directory into this service's Chroma volume.