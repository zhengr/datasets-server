# build with
#   docker build -t some_tag_sse_api -f Dockerfile ../..
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
    && apt-get install -y build-essential unzip wget \
    libicu-dev ffmpeg libavcodec-extra libsndfile1 llvm pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# RUN pip install -U pip
RUN sudo easy_install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /src
COPY services/sse-api/poetry.lock ./services/sse-api/poetry.lock
COPY services/sse-api/pyproject.toml ./services/sse-api/pyproject.toml
COPY libs/libcommon ./libs/libcommon
COPY libs/libapi ./libs/libapi
WORKDIR /src/services/sse-api/
RUN poetry install --no-cache
COPY services/sse-api/src ./src
RUN poetry install --no-cache

ENTRYPOINT ["poetry", "run", "python", "src/sse_api/main.py"]
