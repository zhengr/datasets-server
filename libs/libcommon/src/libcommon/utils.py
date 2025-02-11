# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The HuggingFace Authors.

import base64
import enum
import mimetypes
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from fnmatch import fnmatch
from http import HTTPStatus
from typing import Any, Optional, TypedDict

import orjson
import pandas as pd

from libcommon.exceptions import DatasetInBlockListError


class Status(str, enum.Enum):
    WAITING = "waiting"
    STARTED = "started"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


class Priority(str, enum.Enum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class JobParams(TypedDict):
    dataset: str
    revision: str
    config: Optional[str]
    split: Optional[str]


class JobInfo(TypedDict):
    job_id: str
    type: str
    params: JobParams
    priority: Priority
    difficulty: int


class FlatJobInfo(TypedDict):
    job_id: str
    type: str
    dataset: str
    revision: str
    config: Optional[str]
    split: Optional[str]
    priority: str
    status: str
    difficulty: int
    created_at: datetime


class JobOutput(TypedDict):
    content: Mapping[str, Any]
    http_status: HTTPStatus
    error_code: Optional[str]
    details: Optional[Mapping[str, Any]]
    progress: Optional[float]


class JobResult(TypedDict):
    job_info: JobInfo
    job_runner_version: int
    is_success: bool
    output: Optional[JobOutput]


class SplitHubFile(TypedDict):
    dataset: str
    config: str
    split: str
    url: str
    filename: str
    size: int


Row = dict[str, Any]


class RowItem(TypedDict):
    row_idx: int
    row: Row
    truncated_cells: list[str]


class FeatureItem(TypedDict):
    feature_idx: int
    name: str
    type: dict[str, Any]


class PaginatedResponse(TypedDict):
    features: list[FeatureItem]
    rows: list[RowItem]
    num_rows_total: int
    num_rows_per_page: int


MAX_NUM_ROWS_PER_PAGE = 100


# orjson is used to get rid of errors with datetime (see allenai/c4)
def orjson_default(obj: Any) -> Any:
    if isinstance(obj, bytes):
        # see https://stackoverflow.com/a/40000564/7351594 for example
        # the bytes are encoded with base64, and then decoded as utf-8
        # (ascii only, by the way) to get a string
        return base64.b64encode(obj).decode("utf-8")
    if isinstance(obj, pd.Timestamp):
        return obj.to_pydatetime()
    return str(obj)


def orjson_dumps(content: Any) -> bytes:
    return orjson.dumps(
        content, option=orjson.OPT_UTC_Z | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS, default=orjson_default
    )


def get_datetime(days: Optional[float] = None) -> datetime:
    date = datetime.now(timezone.utc)
    if days is not None:
        date = date - timedelta(days=days)
    return date


def inputs_to_string(
    dataset: str,
    revision: str,
    config: Optional[str] = None,
    split: Optional[str] = None,
    prefix: Optional[str] = None,
) -> str:
    result = f"{dataset},{revision}"
    if config is not None:
        result = f"{result},{config}"
        if split is not None:
            result = f"{result},{split}"
    if prefix is not None:
        result = f"{prefix},{result}"
    return result


def is_image_url(text: str) -> bool:
    is_url = text.startswith("https://") or text.startswith("http://")
    (mime_type, _) = mimetypes.guess_type(text.split("/")[-1].split("?")[0])
    return is_url and mime_type is not None and mime_type.startswith("image/")


def raise_if_blocked(
    dataset: str,
    blocked_datasets: list[str],
) -> None:
    """
    Raise an error if the dataset is in the list of blocked datasets

    Args:
        dataset (`str`):
            A namespace (user or an organization) and a repo name separated
            by a `/`.
        blocked_datasets (`list[str]`):
            The list of blocked datasets. If empty, no dataset is blocked.
            Unix shell-style wildcards are supported in the dataset name, e.g. "open-llm-leaderboard/*"
            to block all the datasets in the `open-llm-leaderboard` namespace. They are not allowed in
            the namespace name.

    Returns:
        `None`
    Raises the following errors:
        - [`libcommon.exceptions.DatasetInBlockListError`]
          If the dataset is in the list of blocked datasets.
    """
    for blocked_dataset in blocked_datasets:
        parts = blocked_dataset.split("/")
        if len(parts) > 2 or not blocked_dataset:
            raise ValueError(
                "The dataset name is not valid. It should be a namespace (user or an organization) and a repo name"
                " separated by a `/`, or a simple repo name for canonical datasets."
            )
        if "*" in parts[0]:
            raise ValueError("The namespace name, or the canonical dataset name, cannot contain a wildcard.")
        if fnmatch(dataset, blocked_dataset):
            raise DatasetInBlockListError(
                "This dataset has been disabled for now. Please open an issue in"
                " https://github.com/huggingface/datasets-server if you want this dataset to be supported."
            )
