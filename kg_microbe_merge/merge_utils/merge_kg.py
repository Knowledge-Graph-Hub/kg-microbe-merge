"""Merging module."""
from typing import Dict

import networkx as nx  # type: ignore
import yaml
from kg_microbe_merge.utils.duckdb_utils import duckdb_load_nodes, remove_duplicate_nodes, write_nodes
from kgx.cli.cli_utils import merge  # type: ignore

import duckdb


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

def duckdb_merge(base_nodes_kg_file, subset_nodes_kg_file):

    # Connect to DuckDB
    con = duckdb.connect()

    duckdb_load_nodes(con, base_nodes_kg_file, subset_nodes_kg_file)

    remove_duplicate_nodes(con)

    write_nodes(con)


