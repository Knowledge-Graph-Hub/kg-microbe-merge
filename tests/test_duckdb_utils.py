"""Test duckdb utilities."""

import filecmp
import os
import unittest
from pathlib import Path

from kg_microbe_merge.utils.duckdb_utils import duckdb_edges_merge, duckdb_nodes_merge

PWD = Path.cwd().resolve()


class TestDuckDBMerge(unittest.TestCase):

    """Test DuckDB merge functions."""

    def setUp(self):
        """Declare Variables for test."""
        self.nodes_file_list = [
            str(PWD / "tests/data/test_nodes_1.tsv"),
            str(PWD / "tests/data/test_nodes_2.tsv"),
        ]
        self.edges_file_list = [
            str(PWD / "tests/data/test_edges_1.tsv"),
            str(PWD / "tests/data/test_edges_2.tsv"),
        ]
        self.output_nodes_file = str(PWD / "tests/data/output/test_nodes_merged.tsv")
        self.output_edges_file = str(PWD / "tests/data/output/test_edges_merged.tsv")
        self.expected_nodes_output = str(PWD / "tests/data/expected_nodes_merged.tsv")
        self.expected_edges_output = str(PWD / "tests/data/expected_edges_merged.tsv")
        self.prioritized_sources = ["ncbitaxon_removed_subset.json", "chebi.json", "uniprot.json"]

    def tearDown(self):
        """Clean up after test."""
        if os.path.exists(self.output_nodes_file):
            os.remove(self.output_nodes_file)
        if os.path.exists(self.output_edges_file):
            os.remove(self.output_edges_file)

    def test_nodes_merge(self):
        """Test nodes merge."""
        # Run the merge function
        duckdb_nodes_merge(self.nodes_file_list, self.output_nodes_file, self.prioritized_sources)

        # Check if the output file was created
        self.assertTrue(os.path.exists(self.output_nodes_file), "Output file was not created")

        # Compare the output with the expected output
        self.assertTrue(
            filecmp.cmp(self.output_nodes_file, self.expected_nodes_output, shallow=False),
            "Output file does not match expected output",
        )

        # Checking the content of the files line by line
        with open(self.output_nodes_file, "r") as output, open(
            self.expected_nodes_output, "r"
        ) as expected:
            output_lines = output.readlines()
            expected_lines = expected.readlines()

            self.assertEqual(
                len(output_lines),
                len(expected_lines),
                "Number of lines in output and expected files do not match",
            )

            

    def test_edges_merge(self):
        """Test edges merge."""
        # Run the merge function
        duckdb_edges_merge(self.edges_file_list, self.output_edges_file)

        # Check if the output file was created
        self.assertTrue(os.path.exists(self.output_edges_file), "Output file was not created")

        # Compare the output with the expected output
        self.assertTrue(
            filecmp.cmp(self.output_edges_file, self.expected_edges_output, shallow=False),
            "Output file does not match expected output",
        )

        # Checking the content of the files line by line
        with open(self.output_edges_file, "r") as output, open(
            self.expected_edges_output, "r"
        ) as expected:
            output_lines = output.readlines()
            expected_lines = expected.readlines()

            self.assertEqual(
                len(output_lines),
                len(expected_lines),
                "Number of lines in output and expected files do not match",
            )

            
