FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app 

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONPATH=/app

RUN apt-get update \
  && apt-get install -y libpq-dev gcc curl ca-certificates \
  && apt-get install -y libglib2.0-0 \
  && apt-get install -y libgl1 \
  && rm -rf /var/lib/apt/lists/*

COPY . .                   
RUN test -f uv.lock || (echo "uv.lock file is missing. Stopping the build." && exit 1)
RUN test -f pyproject.toml || (echo "pyproject file is missing. Stopping the build." && exit 1)
RUN pip install uv
RUN uv run --frozen python --version

CMD ["uv", "run", "--frozen", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]