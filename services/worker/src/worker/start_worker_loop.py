# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The HuggingFace Authors.

import sys

from libcommon.log import init_logging
from libcommon.processing_graph import ProcessingGraph
from libcommon.resources import CacheMongoResource, QueueMongoResource
from libcommon.s3_client import S3Client
from libcommon.storage import (
    init_assets_dir,
    init_duckdb_index_cache_dir,
    init_parquet_metadata_dir,
    init_statistics_cache_dir,
)

from worker.config import AppConfig
from worker.job_runner_factory import JobRunnerFactory
from worker.loop import Loop
from worker.resources import LibrariesResource

if __name__ == "__main__":
    app_config = AppConfig.from_env()

    state_file_path = app_config.worker.state_file_path
    if "--print-worker-state-path" in sys.argv:
        print(state_file_path, flush=True)
    if not state_file_path:
        raise RuntimeError("The worker state file path is not set. Exiting.")

    init_logging(level=app_config.log.level)
    # ^ set first to have logs as soon as possible
    assets_directory = init_assets_dir(directory=app_config.assets.storage_directory)
    parquet_metadata_directory = init_parquet_metadata_dir(directory=app_config.parquet_metadata.storage_directory)
    duckdb_index_cache_directory = init_duckdb_index_cache_dir(directory=app_config.duckdb_index.cache_directory)
    statistics_cache_directory = init_statistics_cache_dir(app_config.descriptive_statistics.cache_directory)

    processing_graph = ProcessingGraph(app_config.processing_graph)
    s3_client = S3Client(
        aws_access_key_id=app_config.s3.access_key_id,
        aws_secret_access_key=app_config.s3.secret_access_key,
        region_name=app_config.s3.region,
        bucket_name=app_config.s3.bucket,
    )

    with (
        LibrariesResource(
            hf_endpoint=app_config.common.hf_endpoint,
            init_hf_datasets_cache=app_config.datasets_based.hf_datasets_cache,
            numba_path=app_config.numba.path,
        ) as libraries_resource,
        CacheMongoResource(
            database=app_config.cache.mongo_database, host=app_config.cache.mongo_url
        ) as cache_resource,
        QueueMongoResource(
            database=app_config.queue.mongo_database, host=app_config.queue.mongo_url
        ) as queue_resource,
    ):
        if not cache_resource.is_available():
            raise RuntimeError("The connection to the cache database could not be established. Exiting.")
        if not queue_resource.is_available():
            raise RuntimeError("The connection to the queue database could not be established. Exiting.")

        job_runner_factory = JobRunnerFactory(
            app_config=app_config,
            processing_graph=processing_graph,
            hf_datasets_cache=libraries_resource.hf_datasets_cache,
            assets_directory=assets_directory,
            parquet_metadata_directory=parquet_metadata_directory,
            duckdb_index_cache_directory=duckdb_index_cache_directory,
            statistics_cache_directory=statistics_cache_directory,
            s3_client=s3_client,
        )
        loop = Loop(
            library_cache_paths=libraries_resource.storage_paths,
            job_runner_factory=job_runner_factory,
            state_file_path=state_file_path,
            app_config=app_config,
            processing_graph=processing_graph,
        )
        loop.run()
