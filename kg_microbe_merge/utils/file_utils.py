"""Utility functions for file operations."""

# Given a path to a directory, look for all files with the extension tar.zip and unzip them all
import tarfile
from pathlib import Path
from typing import List, Union

from click import Tuple


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
    directory: Path, node_paths: List[Path], edge_paths: List[Path]
) -> None:
    """
    Collect node and edge paths from a given directory.

    :param directory: Path to the directory.
    :param node_paths: List of node paths.
    :param edge_paths: List of edge paths.
    :return: None
    """
    for file in directory.iterdir():
        if file.is_file() and file.suffix == ".tsv" and not file.name.startswith("._"):
            if "nodes" in file.name:
                node_paths.append(file)
            elif "edges" in file.name:
                edge_paths.append(file)


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
    transforms_lower = {transform.strip().lower() for transform in subset_transforms[0].split(",")}
    transform_dirs = [
        dir
        for dir in data_dir_path.iterdir()
        if dir.is_dir() and dir.name.lower() in transforms_lower
    ]
    ontology_transforms = transforms_lower - {dir.name.lower() for dir in transform_dirs}

    for directory in transform_dirs:
        node_paths.append(directory / "nodes.tsv")
        edge_paths.append(directory / "edges.tsv")

    if ontology_transforms:
        ontology_dir = data_dir_path / "ontologies"
        collect_paths_from_directory(ontology_dir, node_paths, edge_paths)

    return node_paths, edge_paths


def collect_all_kg_paths(data_dir_path: Path) -> Tuple[List[Path], List[Path]]:
    """
    Get the paths to the nodes and edges files for all KGs.

    :param data_dir_path: Path to the data directory.
    :return: List of node and edge paths.
    """
    node_paths = []
    edge_paths = []
    for directory in data_dir_path.iterdir():
        if directory.is_dir():
            if directory.name != "ontologies":
                node_paths.append(directory / "nodes.tsv")
                edge_paths.append(directory / "edges.tsv")
            else:
                collect_paths_from_directory(directory, node_paths, edge_paths)

    return node_paths, edge_paths
