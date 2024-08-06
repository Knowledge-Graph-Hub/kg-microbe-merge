"""Data test."""

import glob
import os
import unittest

from linkml_runtime.loaders import yaml_loader

from kg_microbe_merge.schema.merge_datamodel import MergeKG

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT, "tests", "data")

EXAMPLE_FILES = glob.glob(os.path.join(DATA_DIR, "test_merge_schema.yaml"))


class TestData(unittest.TestCase):

    """Test data and datamodel."""

    def test_data(self):
        """Data test."""
        for path in EXAMPLE_FILES:
            obj = yaml_loader.load(path, target_class=MergeKG)
            self.assertTrue(obj)
