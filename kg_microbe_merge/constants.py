"""Constants for merge_utilities."""

from pathlib import Path

BASE_NODES_TABLE_NAME = "base_kg_nodes"
SUBSET_NODES_TABLE_NAME = "subset_kg_nodes"
BASE_EDGES_TABLE_NAME = "base_kg_edges"
SUBSET_EDGES_TABLE_NAME = "subset_kg_edges"
NODES_COLUMNS = [
    "id",
    "name",
    "description",
    "category",
    "xref",
    "provided_by",
    "synonym",
    "object",
    "predicate",
    "relation",
    "same_as",
    "subject",
    "subsets",
]
EDGES_COLUMNS = ["subject", "predicate", "object", "relation", "primary_knowledge_source"]

PWD = Path.cwd().resolve()
DATA_DIR = PWD / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
MERGED_DATA_DIR = DATA_DIR / "merged"
MERGED_GRAPH_STATS_FILE = MERGED_DATA_DIR / "merged_graph_stats.yaml"
