# build with
#   docker build -t some_tag_admin -f Dockerfile ../..
FROM python:3.9.15-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    # Versions:
    POETRY_VERSION=1.4.2 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="$PATH:/root/.local/bin"

# Update apt sources in china
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

# System deps:
RUN apt-get update \
    && apt-get install -y build-essential python3-dev make \
    && rm -rf /var/lib/apt/lists/*

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN python -m pip install --upgrade pip -i https://pypi.douban.com/simple
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /src
COPY jobs/cache_maintenance/poetry.lock ./jobs/cache_maintenance/poetry.lock
COPY jobs/cache_maintenance/pyproject.toml ./jobs/cache_maintenance/pyproject.toml
COPY libs/libcommon ./libs/libcommon
WORKDIR /src/jobs/cache_maintenance/
RUN poetry install --no-cache
COPY jobs/cache_maintenance/src ./src
RUN poetry install --no-cache

ENTRYPOINT ["poetry", "run", "python", "src/cache_maintenance/main.py"]
