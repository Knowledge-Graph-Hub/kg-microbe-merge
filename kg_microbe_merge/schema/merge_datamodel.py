# Auto generated from merge_schema.yaml by pythongen.py version: 0.0.1
# Generation date: 2024-08-06T07:55:55
# Schema: KGMergeSchema
#
# id: http://example.org/kg-merge-schema
# description: A schema for the kg-merge configuration.
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from datetime import date, datetime
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import String

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = CurieNamespace('', 'http://example.org/kg-merge-schema/')


# Types

# Class references



@dataclass
class MergeKG(YAMLRoot):
    """
    Configuration for merging knowledge graphs
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/MergeKG")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "MergeKG"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/MergeKG")

    configuration: Optional[Union[dict, "Configuration"]] = None
    merged_graph: Optional[Union[dict, "MergedGraph"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.configuration is not None and not isinstance(self.configuration, Configuration):
            self.configuration = Configuration(**as_dict(self.configuration))

        if self.merged_graph is not None and not isinstance(self.merged_graph, MergedGraph):
            self.merged_graph = MergedGraph(**as_dict(self.merged_graph))

        super().__post_init__(**kwargs)


@dataclass
class Configuration(YAMLRoot):
    """
    Configuration for the merge operation
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Configuration")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Configuration"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Configuration")

    output_directory: Optional[str] = None
    checkpoint: Optional[str] = None
    curie_map: Optional[str] = None
    node_properties: Optional[str] = None
    predicate_mappings: Optional[str] = None
    property_types: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.output_directory is not None and not isinstance(self.output_directory, str):
            self.output_directory = str(self.output_directory)

        if self.checkpoint is not None and not isinstance(self.checkpoint, str):
            self.checkpoint = str(self.checkpoint)

        if self.curie_map is not None and not isinstance(self.curie_map, str):
            self.curie_map = str(self.curie_map)

        if self.node_properties is not None and not isinstance(self.node_properties, str):
            self.node_properties = str(self.node_properties)

        if self.predicate_mappings is not None and not isinstance(self.predicate_mappings, str):
            self.predicate_mappings = str(self.predicate_mappings)

        if self.property_types is not None and not isinstance(self.property_types, str):
            self.property_types = str(self.property_types)

        super().__post_init__(**kwargs)


@dataclass
class MergedGraph(YAMLRoot):
    """
    Details about graphs to be merged.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/MergedGraph")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "MergedGraph"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/MergedGraph")

    name: Optional[str] = None
    source: Optional[Union[Union[dict, "SourceGraph"], List[Union[dict, "SourceGraph"]]]] = empty_list()
    operations: Optional[Union[Union[dict, "Operations"], List[Union[dict, "Operations"]]]] = empty_list()
    destination: Optional[Union[Union[dict, "Destination"], List[Union[dict, "Destination"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if not isinstance(self.source, list):
            self.source = [self.source] if self.source is not None else []
        self.source = [v if isinstance(v, SourceGraph) else SourceGraph(**as_dict(v)) for v in self.source]

        if not isinstance(self.operations, list):
            self.operations = [self.operations] if self.operations is not None else []
        self.operations = [v if isinstance(v, Operations) else Operations(**as_dict(v)) for v in self.operations]

        if not isinstance(self.destination, list):
            self.destination = [self.destination] if self.destination is not None else []
        self.destination = [v if isinstance(v, Destination) else Destination(**as_dict(v)) for v in self.destination]

        super().__post_init__(**kwargs)


@dataclass
class SourceGraph(YAMLRoot):
    """
    Details of a source graph to be merged
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/SourceGraph")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "SourceGraph"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/SourceGraph")

    name: Optional[str] = None
    input: Optional[Union[dict, "InputFiles"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.input is not None and not isinstance(self.input, InputFiles):
            self.input = InputFiles(**as_dict(self.input))

        super().__post_init__(**kwargs)


@dataclass
class InputFiles(YAMLRoot):
    """
    Input files for the source graph
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/InputFiles")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "InputFiles"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/InputFiles")

    format: Optional[str] = None
    filename: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.format is not None and not isinstance(self.format, str):
            self.format = str(self.format)

        if not isinstance(self.filename, list):
            self.filename = [self.filename] if self.filename is not None else []
        self.filename = [v if isinstance(v, str) else str(v) for v in self.filename]

        super().__post_init__(**kwargs)


@dataclass
class Operations(YAMLRoot):
    """
    Details of an operation to perform on the merged graph
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Operations")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Operations"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Operations")

    name: Optional[str] = None
    args: Optional[Union[dict, "OperationArgs"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.args is not None and not isinstance(self.args, OperationArgs):
            self.args = OperationArgs(**as_dict(self.args))

        super().__post_init__(**kwargs)


@dataclass
class OperationArgs(YAMLRoot):
    """
    Arguments for an operation
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/OperationArgs")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "OperationArgs"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/OperationArgs")

    graph_name: Optional[str] = None
    filename: Optional[str] = None
    node_facet_properties: Optional[Union[str, List[str]]] = empty_list()
    edge_facet_properties: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.graph_name is not None and not isinstance(self.graph_name, str):
            self.graph_name = str(self.graph_name)

        if self.filename is not None and not isinstance(self.filename, str):
            self.filename = str(self.filename)

        if not isinstance(self.node_facet_properties, list):
            self.node_facet_properties = [self.node_facet_properties] if self.node_facet_properties is not None else []
        self.node_facet_properties = [v if isinstance(v, str) else str(v) for v in self.node_facet_properties]

        if not isinstance(self.edge_facet_properties, list):
            self.edge_facet_properties = [self.edge_facet_properties] if self.edge_facet_properties is not None else []
        self.edge_facet_properties = [v if isinstance(v, str) else str(v) for v in self.edge_facet_properties]

        super().__post_init__(**kwargs)


@dataclass
class Destination(YAMLRoot):
    """
    Details of a destination for the merged graph
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Destination")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Destination"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Destination")

    format: Optional[str] = None
    compression: Optional[str] = None
    filename: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.format is not None and not isinstance(self.format, str):
            self.format = str(self.format)

        if self.compression is not None and not isinstance(self.compression, str):
            self.compression = str(self.compression)

        if self.filename is not None and not isinstance(self.filename, str):
            self.filename = str(self.filename)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.mergeKG__configuration = Slot(uri=DEFAULT_.configuration, name="mergeKG__configuration", curie=DEFAULT_.curie('configuration'),
                   model_uri=DEFAULT_.mergeKG__configuration, domain=None, range=Optional[Union[dict, Configuration]])

slots.mergeKG__merged_graph = Slot(uri=DEFAULT_.merged_graph, name="mergeKG__merged_graph", curie=DEFAULT_.curie('merged_graph'),
                   model_uri=DEFAULT_.mergeKG__merged_graph, domain=None, range=Optional[Union[dict, MergedGraph]])

slots.configuration__output_directory = Slot(uri=DEFAULT_.output_directory, name="configuration__output_directory", curie=DEFAULT_.curie('output_directory'),
                   model_uri=DEFAULT_.configuration__output_directory, domain=None, range=Optional[str])

slots.configuration__checkpoint = Slot(uri=DEFAULT_.checkpoint, name="configuration__checkpoint", curie=DEFAULT_.curie('checkpoint'),
                   model_uri=DEFAULT_.configuration__checkpoint, domain=None, range=Optional[str])

slots.configuration__curie_map = Slot(uri=DEFAULT_.curie_map, name="configuration__curie_map", curie=DEFAULT_.curie('curie_map'),
                   model_uri=DEFAULT_.configuration__curie_map, domain=None, range=Optional[str])

slots.configuration__node_properties = Slot(uri=DEFAULT_.node_properties, name="configuration__node_properties", curie=DEFAULT_.curie('node_properties'),
                   model_uri=DEFAULT_.configuration__node_properties, domain=None, range=Optional[str])

slots.configuration__predicate_mappings = Slot(uri=DEFAULT_.predicate_mappings, name="configuration__predicate_mappings", curie=DEFAULT_.curie('predicate_mappings'),
                   model_uri=DEFAULT_.configuration__predicate_mappings, domain=None, range=Optional[str])

slots.configuration__property_types = Slot(uri=DEFAULT_.property_types, name="configuration__property_types", curie=DEFAULT_.curie('property_types'),
                   model_uri=DEFAULT_.configuration__property_types, domain=None, range=Optional[str])

slots.mergedGraph__name = Slot(uri=DEFAULT_.name, name="mergedGraph__name", curie=DEFAULT_.curie('name'),
                   model_uri=DEFAULT_.mergedGraph__name, domain=None, range=Optional[str])

slots.mergedGraph__source = Slot(uri=DEFAULT_.source, name="mergedGraph__source", curie=DEFAULT_.curie('source'),
                   model_uri=DEFAULT_.mergedGraph__source, domain=None, range=Optional[Union[Union[dict, SourceGraph], List[Union[dict, SourceGraph]]]])

slots.mergedGraph__operations = Slot(uri=DEFAULT_.operations, name="mergedGraph__operations", curie=DEFAULT_.curie('operations'),
                   model_uri=DEFAULT_.mergedGraph__operations, domain=None, range=Optional[Union[Union[dict, Operations], List[Union[dict, Operations]]]])

slots.mergedGraph__destination = Slot(uri=DEFAULT_.destination, name="mergedGraph__destination", curie=DEFAULT_.curie('destination'),
                   model_uri=DEFAULT_.mergedGraph__destination, domain=None, range=Optional[Union[Union[dict, Destination], List[Union[dict, Destination]]]])

slots.sourceGraph__name = Slot(uri=DEFAULT_.name, name="sourceGraph__name", curie=DEFAULT_.curie('name'),
                   model_uri=DEFAULT_.sourceGraph__name, domain=None, range=Optional[str])

slots.sourceGraph__input = Slot(uri=DEFAULT_.input, name="sourceGraph__input", curie=DEFAULT_.curie('input'),
                   model_uri=DEFAULT_.sourceGraph__input, domain=None, range=Optional[Union[dict, InputFiles]])

slots.inputFiles__format = Slot(uri=DEFAULT_.format, name="inputFiles__format", curie=DEFAULT_.curie('format'),
                   model_uri=DEFAULT_.inputFiles__format, domain=None, range=Optional[str])

slots.inputFiles__filename = Slot(uri=DEFAULT_.filename, name="inputFiles__filename", curie=DEFAULT_.curie('filename'),
                   model_uri=DEFAULT_.inputFiles__filename, domain=None, range=Optional[Union[str, List[str]]])

slots.operations__name = Slot(uri=DEFAULT_.name, name="operations__name", curie=DEFAULT_.curie('name'),
                   model_uri=DEFAULT_.operations__name, domain=None, range=Optional[str])

slots.operations__args = Slot(uri=DEFAULT_.args, name="operations__args", curie=DEFAULT_.curie('args'),
                   model_uri=DEFAULT_.operations__args, domain=None, range=Optional[Union[dict, OperationArgs]])

slots.operationArgs__graph_name = Slot(uri=DEFAULT_.graph_name, name="operationArgs__graph_name", curie=DEFAULT_.curie('graph_name'),
                   model_uri=DEFAULT_.operationArgs__graph_name, domain=None, range=Optional[str])

slots.operationArgs__filename = Slot(uri=DEFAULT_.filename, name="operationArgs__filename", curie=DEFAULT_.curie('filename'),
                   model_uri=DEFAULT_.operationArgs__filename, domain=None, range=Optional[str])

slots.operationArgs__node_facet_properties = Slot(uri=DEFAULT_.node_facet_properties, name="operationArgs__node_facet_properties", curie=DEFAULT_.curie('node_facet_properties'),
                   model_uri=DEFAULT_.operationArgs__node_facet_properties, domain=None, range=Optional[Union[str, List[str]]])

slots.operationArgs__edge_facet_properties = Slot(uri=DEFAULT_.edge_facet_properties, name="operationArgs__edge_facet_properties", curie=DEFAULT_.curie('edge_facet_properties'),
                   model_uri=DEFAULT_.operationArgs__edge_facet_properties, domain=None, range=Optional[Union[str, List[str]]])

slots.destination__format = Slot(uri=DEFAULT_.format, name="destination__format", curie=DEFAULT_.curie('format'),
                   model_uri=DEFAULT_.destination__format, domain=None, range=Optional[str])

slots.destination__compression = Slot(uri=DEFAULT_.compression, name="destination__compression", curie=DEFAULT_.curie('compression'),
                   model_uri=DEFAULT_.destination__compression, domain=None, range=Optional[str])

slots.destination__filename = Slot(uri=DEFAULT_.filename, name="destination__filename", curie=DEFAULT_.curie('filename'),
                   model_uri=DEFAULT_.destination__filename, domain=None, range=Optional[str])
