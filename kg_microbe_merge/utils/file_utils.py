"""Utility functions for file operations."""

# Given a path to a directory, look for all files with the extension tar.zip and unzip them all
from pathlib import Path
import tarfile
from typing import Union


def unzip_files_in_dir(dir_path: Union[str, Path]) -> None:
    """
    Unzip all files with the extension .tar.gz in a directory.

    :param dir_path: Path to the directory containing the .tar.gz files.
    :return: None
    """
    dir_path = Path(dir_path)
    for file in dir_path.iterdir():
        if file.suffix == ".gz" and file.stem.endswith(".tar"):
            extract_dir = dir_path / file.stem.replace('.tar', '')
            if extract_dir.exists() and any(extract_dir.iterdir()):
                print(f"Skipping {file.name}, already extracted.")
                continue
            
            with tarfile.open(file, "r:gz") as tar:
                tar.extractall(path=extract_dir)
                tar.close()
                print(f"Extracted {file.name} to {extract_dir}")