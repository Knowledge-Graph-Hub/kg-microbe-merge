"""Utility functions for file operations."""

# Given a path to a directory, look for all files with the extension tar.zip and unzip them all
import tarfile
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple, Union

from kg_microbe_merge.schema.merge_datamodel import InputFiles, MergedGraph, SourceGraph


def unzip_files_in_dir(dir_path: Union[str, Path]) -> None:
    """
    Unzip all files with the extension .tar.gz in a directory.

    :param dir_path: Path to the directory containing the .tar.gz files.
    :return: None
    """
    dir_path = Path(dir_path)
    for file in dir_path.iterdir():
        if file.suffix == ".gz" and file.stem.endswith(".tar"):
            extract_dir = dir_path / file.stem.replace(".tar", "")
            if extract_dir.exists() and any(extract_dir.iterdir()):
                print(f"Skipping {file.name}, already extracted.")
                continue

            with tarfile.open(file, "r:gz") as tar:
                tar.extractall(path=extract_dir)
                tar.close()
                print(f"Extracted {file.name} to {extract_dir}")


def tarball_files_in_dir(dir_path: Union[str, Path], filename: str) -> None:
    """
    Tarball all files in a directory.

    :param dir_path: Path to the directory containing the files to tarball.
    :return: None
    """
    dir_path = Path(dir_path)
    with tarfile.open(f"{dir_path}/{filename}.tar.gz", "w:gz") as tar:
        for file in dir_path.iterdir():
            tar.add(file, arcname=file.name)
            print(f"Added {file.name} to {dir_path}/{filename}.tar.gz")
    tar.close()


def collect_paths_from_directory(
    directory: Path,
    node_paths: List[Path],
    edge_paths: List[Path],
    merged_graph_object: MergedGraph,
    ontology_transforms: set[str] = None,
) -> None:
    """
    Collect node and edge paths from a given directory.

    :param directory: Path to the directory.
    :param node_paths: List of node paths.
    :param edge_paths: List of edge paths.
    :return: None
    """
    nodes_edges_path_collecter = defaultdict(list)
    source_graph_object_list = []
    if ontology_transforms:
        files_of_interest = [
            file
            for file in directory.iterdir()
            if any(transform in file.name.lower() for transform in ontology_transforms)
            and not file.name.startswith("._")
        ]

    else:
        files_of_interest = [file for file in directory.iterdir() if not file.name.startswith("._")]

    for file in files_of_interest:
        if file.is_file() and file.suffix == ".tsv" and not file.name.startswith("._"):
            if "nodes" in file.name:
                node_paths.append(file)
            elif "edges" in file.name:
                edge_paths.append(file)
            nodes_edges_path_collecter[file.stem.split("_")[0]].append(file)

    source_graph_object_list = [
        SourceGraph(name=key, input=InputFiles(format="tsv", filename=value))
        for key, value in nodes_edges_path_collecter.items()
    ]
    merged_graph_object.source.extend(source_graph_object_list)


def collect_subset_kg_paths(
    subset_transforms: Tuple[str], data_dir_path: Path
) -> Tuple[List[Path], List[Path]]:
    """
    Get the paths to the nodes and edges files for the subset transforms.

    :param subset_transforms: Tuple of subset transforms.
    :param data_dir_path: Path to the data directory.
    :return: List of node and edge paths.
    """
    node_paths = []
    edge_paths = []
    merged_graph_object = MergedGraph(
        name="merged_kg",
    )

    transforms_lower = {transform.strip().lower() for transform in subset_transforms[0].split(",")}
    transform_dirs = [
        dir
        for dir in data_dir_path.iterdir()
        if dir.is_dir() and dir.name.lower() in transforms_lower
    ]
    ontology_transforms = transforms_lower - {dir.name.lower() for dir in transform_dirs}

    for directory in transform_dirs:
        node_path = directory / "nodes.tsv"
        edge_path = directory / "edges.tsv"
        source_graph_object = SourceGraph(
            name=directory.name,
            input=InputFiles(format="tsv", filename=[node_path, edge_path]),
        )
        merged_graph_object.source.append(source_graph_object)
        node_paths.append(node_path)
        edge_paths.append(edge_path)

    if ontology_transforms:
        ontology_dir = data_dir_path / "ontologies"
        collect_paths_from_directory(
            ontology_dir, node_paths, edge_paths, merged_graph_object, ontology_transforms
        )

    return node_paths, edge_paths, merged_graph_object


def collect_all_kg_paths(data_dir_path: Path) -> Tuple[List[Path], List[Path]]:
    """
    Get the paths to the nodes and edges files for all KGs.

    :param data_dir_path: Path to the data directory.
    :return: List of node and edge paths.
    """
    node_paths = []
    edge_paths = []
    merged_graph_object = MergedGraph(
        name="merged_kg",
    )
    for directory in data_dir_path.iterdir():
        if directory.is_dir():
            if directory.name != "ontologies":
                node_path = directory / "nodes.tsv"
                edge_path = directory / "edges.tsv"
                node_paths.append(node_path)
                edge_paths.append(edge_path)
                source_graph_object = SourceGraph(
                    name=directory.name,
                    input=InputFiles(format="tsv", filename=[node_path, edge_path]),
                )
                merged_graph_object.source.append(source_graph_object)
            else:
                collect_paths_from_directory(directory, node_paths, edge_paths, merged_graph_object)

    return node_path, edge_paths, merged_graph_object
