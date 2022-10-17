# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The HuggingFace Authors.

import os
from typing import Tuple

from libutils.utils import get_str_value

DEFAULT_HF_ENDPOINT: str = "https://huggingface.co"
DEFAULT_HF_TOKEN: str = ""
DEFAULT_MONGO_CACHE_DATABASE: str = "datasets_server_cache_test"
DEFAULT_MONGO_QUEUE_DATABASE: str = "datasets_server_queue_test"
DEFAULT_MONGO_URL: str = "mongodb://localhost:27017"

HF_ENDPOINT = get_str_value(d=os.environ, key="HF_ENDPOINT", default=DEFAULT_HF_ENDPOINT)
HF_TOKEN = get_str_value(d=os.environ, key="HF_TOKEN", default=DEFAULT_HF_TOKEN)
MONGO_CACHE_DATABASE = get_str_value(d=os.environ, key="MONGO_CACHE_DATABASE", default=DEFAULT_MONGO_CACHE_DATABASE)
MONGO_QUEUE_DATABASE = get_str_value(d=os.environ, key="MONGO_QUEUE_DATABASE", default=DEFAULT_MONGO_QUEUE_DATABASE)
MONGO_URL = get_str_value(d=os.environ, key="MONGO_URL", default=DEFAULT_MONGO_URL)


def get_default_config_split(dataset: str) -> Tuple[str, str, str]:
    config = dataset.replace("/", "--")
    split = "train"
    return dataset, config, split
