# Auto generated from merge_schema.yaml by pythongen.py version: 0.0.1
# Generation date: 2024-07-31T17:23:28
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
from linkml_runtime.linkml_model.types import Boolean, String
from linkml_runtime.utils.metamodelcore import Bool

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
class Configuration(YAMLRoot):
    """
    Configuration settings for the merged graph.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Configuration")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Configuration"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Configuration")

    output_directory: Optional[str] = None
    checkpoint: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.output_directory is not None and not isinstance(self.output_directory, str):
            self.output_directory = str(self.output_directory)

        if self.checkpoint is not None and not isinstance(self.checkpoint, Bool):
            self.checkpoint = Bool(self.checkpoint)

        super().__post_init__(**kwargs)


@dataclass
class Source(YAMLRoot):
    """
    Source information for the graphs.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Source")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Source"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Source")

    name: Optional[str] = None
    input: Optional[Union[dict, "Input"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.input is not None and not isinstance(self.input, Input):
            self.input = Input(**as_dict(self.input))

        super().__post_init__(**kwargs)


@dataclass
class Input(YAMLRoot):
    """
    Input file details.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Input")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Input"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Input")

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
class Operation(YAMLRoot):
    """
    Operations to be performed on the graph.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Operation")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Operation"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Operation")

    name: Optional[str] = None
    args: Optional[Union[dict, "Args"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.args is not None and not isinstance(self.args, Args):
            self.args = Args(**as_dict(self.args))

        super().__post_init__(**kwargs)


@dataclass
class Args(YAMLRoot):
    """
    Arguments for operations.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Args")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Args"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/Args")

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
    Destination details for the merged graph.
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


@dataclass
class MergedGraph(YAMLRoot):
    """
    Details of the merged graph.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/MergedGraph")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "MergedGraph"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/kg-merge-schema/MergedGraph")

    name: Optional[str] = None
    source: Optional[Union[Union[dict, Source], List[Union[dict, Source]]]] = empty_list()
    operations: Optional[Union[Union[dict, Operation], List[Union[dict, Operation]]]] = empty_list()
    destination: Optional[Union[Union[dict, Destination], List[Union[dict, Destination]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if not isinstance(self.source, list):
            self.source = [self.source] if self.source is not None else []
        self.source = [v if isinstance(v, Source) else Source(**as_dict(v)) for v in self.source]

        if not isinstance(self.operations, list):
            self.operations = [self.operations] if self.operations is not None else []
        self.operations = [v if isinstance(v, Operation) else Operation(**as_dict(v)) for v in self.operations]

        if not isinstance(self.destination, list):
            self.destination = [self.destination] if self.destination is not None else []
        self.destination = [v if isinstance(v, Destination) else Destination(**as_dict(v)) for v in self.destination]

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.output_directory = Slot(uri=DEFAULT_.output_directory, name="output_directory", curie=DEFAULT_.curie('output_directory'),
                   model_uri=DEFAULT_.output_directory, domain=None, range=Optional[str])

slots.checkpoint = Slot(uri=DEFAULT_.checkpoint, name="checkpoint", curie=DEFAULT_.curie('checkpoint'),
                   model_uri=DEFAULT_.checkpoint, domain=None, range=Optional[str])

slots.name = Slot(uri=DEFAULT_.name, name="name", curie=DEFAULT_.curie('name'),
                   model_uri=DEFAULT_.name, domain=None, range=Optional[str])

slots.input = Slot(uri=DEFAULT_.input, name="input", curie=DEFAULT_.curie('input'),
                   model_uri=DEFAULT_.input, domain=None, range=Optional[str])

slots.format = Slot(uri=DEFAULT_.format, name="format", curie=DEFAULT_.curie('format'),
                   model_uri=DEFAULT_.format, domain=None, range=Optional[str])

slots.filename = Slot(uri=DEFAULT_.filename, name="filename", curie=DEFAULT_.curie('filename'),
                   model_uri=DEFAULT_.filename, domain=None, range=Optional[str])

slots.source = Slot(uri=DEFAULT_.source, name="source", curie=DEFAULT_.curie('source'),
                   model_uri=DEFAULT_.source, domain=None, range=Optional[str])

slots.operations = Slot(uri=DEFAULT_.operations, name="operations", curie=DEFAULT_.curie('operations'),
                   model_uri=DEFAULT_.operations, domain=None, range=Optional[str])

slots.destination = Slot(uri=DEFAULT_.destination, name="destination", curie=DEFAULT_.curie('destination'),
                   model_uri=DEFAULT_.destination, domain=None, range=Optional[str])

slots.graph_name = Slot(uri=DEFAULT_.graph_name, name="graph_name", curie=DEFAULT_.curie('graph_name'),
                   model_uri=DEFAULT_.graph_name, domain=None, range=Optional[str])

slots.node_facet_properties = Slot(uri=DEFAULT_.node_facet_properties, name="node_facet_properties", curie=DEFAULT_.curie('node_facet_properties'),
                   model_uri=DEFAULT_.node_facet_properties, domain=None, range=Optional[str])

slots.edge_facet_properties = Slot(uri=DEFAULT_.edge_facet_properties, name="edge_facet_properties", curie=DEFAULT_.curie('edge_facet_properties'),
                   model_uri=DEFAULT_.edge_facet_properties, domain=None, range=Optional[str])

slots.compression = Slot(uri=DEFAULT_.compression, name="compression", curie=DEFAULT_.curie('compression'),
                   model_uri=DEFAULT_.compression, domain=None, range=Optional[str])

slots.configuration__output_directory = Slot(uri=DEFAULT_.output_directory, name="configuration__output_directory", curie=DEFAULT_.curie('output_directory'),
                   model_uri=DEFAULT_.configuration__output_directory, domain=None, range=Optional[str])

slots.configuration__checkpoint = Slot(uri=DEFAULT_.checkpoint, name="configuration__checkpoint", curie=DEFAULT_.curie('checkpoint'),
                   model_uri=DEFAULT_.configuration__checkpoint, domain=None, range=Optional[Union[bool, Bool]])

slots.source__name = Slot(uri=DEFAULT_.name, name="source__name", curie=DEFAULT_.curie('name'),
                   model_uri=DEFAULT_.source__name, domain=None, range=Optional[str])

slots.source__input = Slot(uri=DEFAULT_.input, name="source__input", curie=DEFAULT_.curie('input'),
                   model_uri=DEFAULT_.source__input, domain=None, range=Optional[Union[dict, Input]])

slots.input__format = Slot(uri=DEFAULT_.format, name="input__format", curie=DEFAULT_.curie('format'),
                   model_uri=DEFAULT_.input__format, domain=None, range=Optional[str])

slots.input__filename = Slot(uri=DEFAULT_.filename, name="input__filename", curie=DEFAULT_.curie('filename'),
                   model_uri=DEFAULT_.input__filename, domain=None, range=Optional[Union[str, List[str]]])

slots.operation__name = Slot(uri=DEFAULT_.name, name="operation__name", curie=DEFAULT_.curie('name'),
                   model_uri=DEFAULT_.operation__name, domain=None, range=Optional[str])

slots.operation__args = Slot(uri=DEFAULT_.args, name="operation__args", curie=DEFAULT_.curie('args'),
                   model_uri=DEFAULT_.operation__args, domain=None, range=Optional[Union[dict, Args]])

slots.args__graph_name = Slot(uri=DEFAULT_.graph_name, name="args__graph_name", curie=DEFAULT_.curie('graph_name'),
                   model_uri=DEFAULT_.args__graph_name, domain=None, range=Optional[str])

slots.args__filename = Slot(uri=DEFAULT_.filename, name="args__filename", curie=DEFAULT_.curie('filename'),
                   model_uri=DEFAULT_.args__filename, domain=None, range=Optional[str])

slots.args__node_facet_properties = Slot(uri=DEFAULT_.node_facet_properties, name="args__node_facet_properties", curie=DEFAULT_.curie('node_facet_properties'),
                   model_uri=DEFAULT_.args__node_facet_properties, domain=None, range=Optional[Union[str, List[str]]])

slots.args__edge_facet_properties = Slot(uri=DEFAULT_.edge_facet_properties, name="args__edge_facet_properties", curie=DEFAULT_.curie('edge_facet_properties'),
                   model_uri=DEFAULT_.args__edge_facet_properties, domain=None, range=Optional[Union[str, List[str]]])

slots.destination__format = Slot(uri=DEFAULT_.format, name="destination__format", curie=DEFAULT_.curie('format'),
                   model_uri=DEFAULT_.destination__format, domain=None, range=Optional[str])

slots.destination__compression = Slot(uri=DEFAULT_.compression, name="destination__compression", curie=DEFAULT_.curie('compression'),
                   model_uri=DEFAULT_.destination__compression, domain=None, range=Optional[str])

slots.destination__filename = Slot(uri=DEFAULT_.filename, name="destination__filename", curie=DEFAULT_.curie('filename'),
                   model_uri=DEFAULT_.destination__filename, domain=None, range=Optional[str])

slots.mergedGraph__name = Slot(uri=DEFAULT_.name, name="mergedGraph__name", curie=DEFAULT_.curie('name'),
                   model_uri=DEFAULT_.mergedGraph__name, domain=None, range=Optional[str])

slots.mergedGraph__source = Slot(uri=DEFAULT_.source, name="mergedGraph__source", curie=DEFAULT_.curie('source'),
                   model_uri=DEFAULT_.mergedGraph__source, domain=None, range=Optional[Union[Union[dict, Source], List[Union[dict, Source]]]])

slots.mergedGraph__operations = Slot(uri=DEFAULT_.operations, name="mergedGraph__operations", curie=DEFAULT_.curie('operations'),
                   model_uri=DEFAULT_.mergedGraph__operations, domain=None, range=Optional[Union[Union[dict, Operation], List[Union[dict, Operation]]]])

slots.mergedGraph__destination = Slot(uri=DEFAULT_.destination, name="mergedGraph__destination", curie=DEFAULT_.curie('destination'),
                   model_uri=DEFAULT_.mergedGraph__destination, domain=None, range=Optional[Union[Union[dict, Destination], List[Union[dict, Destination]]]])
