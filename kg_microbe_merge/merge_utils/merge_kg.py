"""Merging module."""

from pathlib import Path
from typing import Dict, List, Union

import networkx as nx  # type: ignore
import yaml
from kgx.cli.cli_utils import merge  # type: ignore

from kg_microbe_merge.utils.duckdb_utils import (
    duckdb_edges_merge,
    duckdb_nodes_merge,
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
) -> None:
    """
    Merge nodes and edges tables using DuckDB.

    :param nodes_files_path: List of paths to nodes files.
    :param edges_files_path: List of paths to edges files.
    :return: None
    """
    # TODO: Get priority sources dynamically from the ontologies transform
    priority_sources = ["go.json", "chebi.json", "ncbitaxon_removed_subset.json"]

    # Merge nodes
    duckdb_nodes_merge(nodes_files_path, merge_nodes_output_path, priority_sources)

    # Merge edges
    duckdb_edges_merge(edges_files_path, merged_edges_output_path)


# def duckdb_merge(
#     base_kg_nodes_file, subset_kg_nodes_file, base_kg_edges_file, subset_kg_edges_file
# ):

#     # Connect to DuckDB
#     con = duckdb.connect()
# Merge nodes
# duckdb_prepare_tables(
#     con,
#     base_kg_nodes_file,
#     subset_kg_nodes_file,
#     BASE_NODES_TABLE_NAME,
#     SUBSET_NODES_TABLE_NAME,
#     NODES_COLUMNS,
# )
# merge_kg_nodes,duplicate_nodes = merge_kg_tables(
#     con, NODES_COLUMNS, BASE_NODES_TABLE_NAME, SUBSET_NODES_TABLE_NAME, "nodes"
# )
# write_file(con, NODES_COLUMNS, "merge_kg_nodes.tsv", merge_kg_nodes)
# write_file(con, NODES_COLUMNS, "duplicate_kg_nodes.tsv", duplicate_nodes)

# # Merge edges
# duckdb_prepare_tables(
#     con,
#     base_kg_edges_file,
#     subset_kg_edges_file,
#     BASE_EDGES_TABLE_NAME,
#     SUBSET_EDGES_TABLE_NAME,
#     EDGES_COLUMNS,
# )
# merge_kg_edges, duplicate_edges = merge_kg_tables(
#     con, EDGES_COLUMNS, BASE_EDGES_TABLE_NAME, SUBSET_EDGES_TABLE_NAME, "edges"
# )
# write_file(con, EDGES_COLUMNS, "merge_kg_edges.tsv", merge_kg_edges)
# write_file(con, EDGES_COLUMNS, "duplicate_kg_edges.tsv", duplicate_edges)
