FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
RUN --mount=type=cache,target=/root/.cache/pip python -c "import subprocess,sys,tomllib; p=tomllib.load(open('pyproject.toml','rb')); subprocess.check_call([sys.executable,'-m','pip','install','hatchling',*p['project']['dependencies']])"
COPY src ./src
RUN pip install --no-deps --no-build-isolation .
ENV CUBICLE_MCP_HOST=0.0.0.0 CUBICLE_MCP_PORT=8765
CMD ["cubicle", "mcp", "--transport", "streamable-http"]
