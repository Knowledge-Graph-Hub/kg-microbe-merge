"""Merging module."""

import csv
import os
from pathlib import Path
from typing import Dict, List, Union

import networkx as nx  # type: ignore
import yaml
from kgx.cli.cli_utils import merge  # type: ignore

from kg_microbe_merge.constants import MERGED_DATA_DIR
from kg_microbe_merge.utils.duckdb_utils import (
    duckdb_edges_merge,
    duckdb_nodes_merge,
)
from kg_microbe_merge.utils.file_utils import tarball_files_in_dir

# Set MALLOC_CONF environment variable to optimize memory allocation (jemalloc) in duckdb.
"""
Here are some commonly used jemalloc options that you might find useful:

narenas: Sets the number of arenas. More arenas can reduce contention
    in multi-threaded applications but may increase memory usage.
lg_chunk: Sets the chunk size. Larger chunks can reduce fragmentation but may increase memory usage.
dirty_decay_ms: Controls the time (in milliseconds) before dirty pages are purged.
    Lower values can reduce memory usage at the cost of performance.
muzzy_decay_ms: Similar to dirty_decay_ms, but for "muzzy" pages (pages that have been decommitted but not yet purged).
background_thread: Enables or disables background threads for purging unused memory.
    Setting this to true can improve performance by offloading purging work to background threads.

"""
os.environ["MALLOC_CONF"] = (
    f"narenas:{os.cpu_count()},lg_chunk:21,background_thread:true,dirty_decay_ms:10000,muzzy_decay_ms:10000"
)


def parse_load_config(yaml_file: str) -> Dict:
    """
    Parse load config YAML.

    :param yaml_file: A string pointing to a KGX compatible config YAML.
    :return: Dict: The config as a dictionary.
    """
    with open(yaml_file) as yamlf:
        config = yaml.safe_load(yamlf)  # , Loader=yaml.FullLoader)
    return config


def load_and_merge(yaml_file: str, processes: int = 1) -> nx.MultiDiGraph:
    """
    Load and merge sources defined in the config YAML.

    :param yaml_file: A string pointing to a KGX compatible config YAML.
    :param processes: Number of processes to use.
    :return: networkx.MultiDiGraph: The merged graph.

    """
    merged_graph = merge(yaml_file, processes=processes)
    return merged_graph


def duckdb_merge(
    nodes_files_path: List[Union[str, Path]],
    edges_files_path: List[Union[str, Path]],
    merge_nodes_output_path: Union[str, Path],
    merged_edges_output_path: Union[str, Path],
    nodes_batch_size: int = 100000,
    edges_batch_size: int = 2000000,
) -> None:
    """
    Merge nodes and edges tables using DuckDB.

    :param nodes_files_path: List of paths to nodes files.
    :param edges_files_path: List of paths to edges files.
    :return: None
    """
    # For all files in the nodes_files_path which has 'ontologies' dir in path,
    # get the value of the `provided_by` column in the tsv file and add it to the priority_sources list

    priority_sources = []
    ontology_nodes_paths = [
        Path(file_path) for file_path in nodes_files_path if "ontologies" in str(file_path)
    ]
    for file_path in ontology_nodes_paths:
        with file_path.open(newline="") as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter="\t")
            for row in reader:
                provided_by_value = row.get("provided_by")
                if provided_by_value:
                    priority_sources.append(provided_by_value)
                    break  # We only need the value from one row

    # Merge nodes
    duckdb_nodes_merge(
        nodes_files_path, merge_nodes_output_path, priority_sources, nodes_batch_size
    )

    # Merge edges
    duckdb_edges_merge(edges_files_path, merged_edges_output_path, edges_batch_size)

    # Tarball all files in a directory
    tarball_files_in_dir(MERGED_DATA_DIR, "merged_kg")
