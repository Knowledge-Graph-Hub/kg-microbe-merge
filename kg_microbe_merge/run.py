"""Drive KG download, transform, merge steps."""

import os
import tempfile
from pathlib import Path
from pprint import pprint
from typing import Union

import click
from linkml_runtime.dumpers import yaml_dumper

from kg_microbe_merge.constants import MERGED_DATA_DIR, MERGED_GRAPH_STATS_FILE, RAW_DATA_DIR
from kg_microbe_merge.schema.merge_datamodel import Configuration, Destination, MergeKG, Operations
from kg_microbe_merge.utils.file_utils import (
    collect_all_kg_paths,
    collect_subset_kg_paths,
    unzip_files_in_dir,
)

try:
    from kg_chat.app import create_app
    from kg_chat.implementations import DuckDBImplementation, Neo4jImplementation
    from kg_chat.main import KnowledgeGraphChat
except ImportError:
    # Handle the case where kg-chat is not installed
    create_app = None
    DuckDBImplementation = None
    Neo4jImplementation = None
    KnowledgeGraphChat = None

from kg_microbe_merge import download as kg_download
from kg_microbe_merge.merge import duckdb_merge, load_and_merge
from kg_microbe_merge.query import parse_query_yaml, result_dict_to_tsv, run_query

database_options = click.option(
    "--database",
    "-d",
    type=click.Choice(["neo4j", "duckdb"], case_sensitive=False),
    help="Database to use.",
    default="duckdb",
)
data_dir_option = click.option(
    "--data-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory containing the data.",
    required=True,
)


@click.group()
def main():
    """CLI."""
    pass


@main.command()
@click.option(
    "yaml_file", "-y", required=True, default="download.yaml", type=click.Path(exists=True)
)
@click.option("output_dir", "-o", required=True, default="data/raw")
@click.option(
    "snippet_only",
    "-x",
    is_flag=True,
    default=False,
    help="Download only the first 5 kB of each (uncompressed) source,\
    for testing and file checks [false]",
)
@click.option(
    "ignore_cache",
    "-i",
    is_flag=True,
    default=False,
    help="ignore cache and download files even if they exist [false]",
)
def download(*args, **kwargs) -> None:
    """
    Download from list of URLs (default: download.yaml) into data directory (default: data/raw).

    :param yaml_file: Specify the YAML file containing a list of datasets to download.
    :param output_dir: A string pointing to the directory to download data to.
    :param snippet_only: Download 5 kB of each uncompressed source, for testing and file checks.
    :param ignore_cache: If specified, will ignore existing files and download again.
    :return: None
    """
    Path(RAW_DATA_DIR).mkdir(parents=True, exist_ok=True)
    kg_download(*args, **kwargs)

    return None


@main.command()
@click.option("yaml", "-y", type=click.Path(exists=True), required=False)
@click.option("processes", "-p", default=1, type=int)
@click.option("--merge-tool", "-m", default="kgx", type=click.Choice(["kgx", "duckdb"]))
@click.option("--data-dir", "-d", type=click.Path(exists=True), default=RAW_DATA_DIR)
@click.option("--subset-transforms", "-s", multiple=True)
@click.option("--merge-label", "-l", default="merged-kg")
@click.option("--nodes-batch-size", "-n", type=int, default=100000)
@click.option("--edges-batch-size", "-e", type=int, default=2000000)
def merge(
    yaml: str,
    processes: int,
    merge_tool: str,
    data_dir: str,
    subset_transforms: tuple,
    merge_label: str,
    nodes_batch_size: int,
    edges_batch_size: int,
) -> None:
    """
    Use KGX to load subgraphs to create a merged graph.

    :param yaml: A YAML file containing a list of datasets to load.
    :param processes: Number of processes to use.
    :param merge_tool: The tool to use for merging.
    :param data_dir: The directory containing the data.
    :param transforms: The transforms to apply.
    :param nodes_batch_size: The batch size for nodes.
    :param edges_batch_size: The batch size for edges.
    :return: None.
    """
    # make dir if not exists: MERGED_DATA_DIR
    Path(MERGED_DATA_DIR).mkdir(parents=True, exist_ok=True)
    data_dir_path = Path(data_dir)
    unzip_files_in_dir(data_dir_path)
    node_paths = []
    edge_paths = []
    merge_configuration = Configuration(output_directory=MERGED_DATA_DIR, checkpoint=False)
    merge_kg_object = MergeKG(configuration=merge_configuration)

    if subset_transforms:
        node_paths, edge_paths, merged_graph_object = collect_subset_kg_paths(
            subset_transforms, data_dir_path
        )
    else:
        node_paths, edge_paths, merged_graph_object = collect_all_kg_paths(data_dir_path)

    merge_kg_object.merged_graph = merged_graph_object
    if merge_tool == "duckdb":
        if merge_label:
            merged_nodes_output_path = MERGED_DATA_DIR / merge_label / "nodes.tsv"
            merged_edges_output_path = MERGED_DATA_DIR / merge_label / "edges.tsv"
        else:
            merged_nodes_output_path = MERGED_DATA_DIR / "nodes.tsv"
            merged_edges_output_path = MERGED_DATA_DIR / "edges.tsv"

        duckdb_merge(
            node_paths,
            edge_paths,
            merged_nodes_output_path,
            merged_edges_output_path,
            nodes_batch_size,
            edges_batch_size,
        )
        # duckdb_merge(base_nodes, subset_nodes, base_edges, subset_edges)
    else:
        if not yaml:
            merge_kg_object.merged_graph.operations = Operations(
                name="merged-kg-tsv",
                args={
                    "graph_name": "merged-kg",
                    "filename": f"{MERGED_GRAPH_STATS_FILE}",
                    "node_facet_properties": ["provided_by"],
                    "edge_facet_properties": ["provided_by", "source"],
                },
            )
            merge_kg_object.merged_graph.destination = Destination(
                format="tsv", compression="tar.gz", filename="merged_kg"
            )
            # yaml = "tmp.yaml"
            # yaml_dumper.dump(merge_kg_object, yaml)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tmp_file:
                tmp_file_path = tmp_file.name
                yaml_dumper.dump(merge_kg_object, tmp_file_path)

                print(f"Temporary file created at: {tmp_file_path}")
        load_and_merge(tmp_file_path, processes)
        os.remove(tmp_file_path)


@main.command()
@click.option("yaml", "-y", required=True, default=None, multiple=False)
@click.option("output_dir", "-o", default="data/queries/")
def query(
    yaml: str,
    output_dir: str,
    query_key: str = "query",
    endpoint_key: str = "endpoint",
    outfile_ext: str = ".tsv",
) -> None:
    """
    Perform a query of knowledge graph using a class contained in query_utils.

    :param yaml: A YAML file containing a SPARQL query (see queries/sparql/ for examples)
    :param output_dir: Directory to output results of query
    :param query_key: the key in the yaml file containing the query string
    :param endpoint_key: the key in the yaml file containing the sparql endpoint URL
    :param outfile_ext: file extension for output file [.tsv]
    :return: None.
    """
    query = parse_query_yaml(yaml)
    result_dict = run_query(query=query[query_key], endpoint=query[endpoint_key])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    outfile = os.path.join(output_dir, os.path.splitext(os.path.basename(yaml))[0] + outfile_ext)
    result_dict_to_tsv(result_dict, outfile)


@main.command()
@click.option(
    "nodes",
    "-n",
    help="nodes KGX TSV file",
    default="data/merged/nodes.tsv",
    type=click.Path(exists=True),
)
@click.option(
    "edges",
    "-e",
    help="edges KGX TSV file",
    default="data/merged/edges.tsv",
    type=click.Path(exists=True),
)
@click.option(
    "output_dir", "-o", help="output directory", default="data/holdouts/", type=click.Path()
)
@click.option(
    "train_fraction",
    "-t",
    help="fraction of input graph to use in training graph [0.8]",
    default=0.8,
    type=float,
)
@click.option("validation", "-v", help="make validation set", is_flag=True, default=False)
def holdouts(*args, **kwargs) -> None:
    """
    Make holdouts for ML training.

    Given a graph (from formatted node and edge TSVs), output positive edges and negative
    edges for use in machine learning.

    To generate positive edges: a set of test positive edges equal in number to
    [(1 - train_fraction) * number of edges in input graph] are randomly selected from
    the edges in the input graph that is not part of a minimal spanning tree, such that
    removing the edge does not create new components. These edges are emitting as
    positive test edges. (If -v == true, the test positive edges are divided equally to
    yield test and validation positive edges.) These edges are then removed from the
    edges of the input graph, and these are emitted as the training edges.

    Negative edges are selected by randomly selecting pairs of nodes that are not
    connected by an edge in the input graph. The number of negative edges emitted is
    equal to the number of positive edges emitted above.

    Outputs these files in [output_dir]:
        pos_train_edges.tsv - positive edges for training (this is the input graph with
                      test [and validation] positive edges removed)
        pos_test_edges.tsv - positive edges for testing
        pos_valid_edges.tsv (optional) - positive edges for validation
        neg_train.tsv - a set of edges not present in input graph for training
        neg_test.tsv - a set of edges not present in input graph for testing
        neg_valid.tsv (optional) - a set of edges not present in input graph for
                      validation

    :param nodes:   nodes for input graph, in KGX TSV format [data/merged/nodes.tsv]
    :param edges:   edges for input graph, in KGX TSV format [data/merged/edges.tsv]
    :param output_dir:     directory to output edges and new graph [data/edges/]
    :param train_fraction: fraction of edges to emit as training [0.8]
    :param validation:     should we make validation edges? [False]

    """
    # make_holdouts(*args, **kwargs)
    raise NotImplementedError("This function is not yet implemented.")


if create_app:
    # ! kg-chat must be installed for these CLI commands to work.

    @main.command("import")
    @database_options
    @data_dir_option
    def import_kg_click(database: str = "duckdb", data_dir: str = None):
        """Run the kg-chat's demo command."""
        if not data_dir:
            raise ValueError(
                "Data directory is required. This typically contains the KGX tsv files."
            )
        if database == "neo4j":
            impl = Neo4jImplementation(data_dir=data_dir)
            impl.load_kg()
        elif database == "duckdb":
            impl = DuckDBImplementation(data_dir=data_dir)
            impl.load_kg()
        else:
            raise ValueError(f"Database {database} not supported.")

    @main.command("test-query")
    @database_options
    @data_dir_option
    def test_query_click(database: str = "duckdb", data_dir: str = None):
        """Run the kg-chat's demo command."""
        if database == "neo4j":
            impl = Neo4jImplementation(data_dir=data_dir)
            query = "MATCH (n) RETURN n LIMIT 10"
            result = impl.execute_query(query)
            for record in result:
                print(record)
        elif database == "duckdb":
            impl = DuckDBImplementation(data_dir=data_dir)
            query = "SELECT * FROM nodes LIMIT 10"
            result = impl.execute_query(query)
            for record in result:
                print(record)
        else:
            raise ValueError(f"Database {database} not supported.")

    @main.command("show-schema")
    @database_options
    @data_dir_option
    def show_schema_click(database: str = "duckdb", data_dir: str = None):
        """Run the kg-chat's chat command."""
        if database == "neo4j":
            impl = Neo4jImplementation(data_dir=data_dir)
            impl.show_schema()
        elif database == "duckdb":
            impl = DuckDBImplementation(data_dir=data_dir)
            impl.show_schema()
        else:
            raise ValueError(f"Database {database} not supported.")

    @main.command("app")
    @database_options
    @click.option("--debug", is_flag=True, help="Run the app in debug mode.")
    @data_dir_option
    def run_app_click(database: str = "duckdb", data_dir: str = None, debug: bool = False):
        """Run the kg-chat's chat command."""
        if database == "neo4j":
            impl = Neo4jImplementation(data_dir=data_dir)
            kgc = KnowledgeGraphChat(impl)
        elif database == "duckdb":
            impl = DuckDBImplementation(data_dir=data_dir)
            kgc = KnowledgeGraphChat(impl)
        else:
            raise ValueError(f"Database {database} not supported.")

        app = create_app(kgc)
        # use_reloader=False to avoid running the app twice in debug mode
        app.run(debug=debug, use_reloader=False)

    @main.command("chat")
    @database_options
    @data_dir_option
    def run_chat_click(database: str = "duckdb", data_dir: str = None, debug: bool = False):
        """Run the kg-chat's chat command."""
        if database == "neo4j":
            impl = Neo4jImplementation(data_dir=data_dir)
            kgc = KnowledgeGraphChat(impl)
            kgc.chat()
        elif database == "duckdb":
            impl = DuckDBImplementation(data_dir=data_dir)
            kgc = KnowledgeGraphChat(impl)
            kgc.chat()
        else:
            raise ValueError(f"Database {database} not supported.")

    @main.command("qna")
    @database_options
    @click.argument("query", type=str, required=True)
    @data_dir_option
    def qna_click(query: str, data_dir: Union[str, Path], database: str = "duckdb"):
        """Run the kg-chat's chat command."""
        if database == "neo4j":
            impl = Neo4jImplementation(data_dir=data_dir)
            response = impl.get_human_response(query, impl)
            pprint(response)
        elif database == "duckdb":
            impl = DuckDBImplementation(data_dir=data_dir)
            response = impl.get_human_response(query)
            pprint(response)
        else:
            raise ValueError(f"Database {database} not supported.")


if __name__ == "__main__":
    main()
