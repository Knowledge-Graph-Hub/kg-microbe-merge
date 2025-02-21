# Instructions to build KGs within the KG-Microbe framework

### Purpose: 
This page details the steps necessary to construct a KG within the KG-Microbe framework.

##### Relevant GitHub Repositories:
- [uniprot2s3](https://github.com/Knowledge-Graph-Hub/uniprot2s3.git) 
- [kg-microbe](https://github.com/Knowledge-Graph-Hub/kg-microbe.git) 
- [kg-microbe-merge](https://github.com/Knowledge-Graph-Hub/kg-microbe-merge.git) 

### Build Process

#### Step 1: Functional Data Download
##### Repository: uniprot2s3

This step queries the UniProt API for microbial and human functional annotation data. 

```
!git clone git@github.com:Knowledge-Graph-Hub/uniprot2s3.git
!make all
```
##### Outputs
- Location: S3
- File: uniprot_proteomes.tar.gz

To create the human raw file, the "human_query" branch must be cloned:

```
!git clone -b human_query git@github.com:Knowledge-Graph-Hub/uniprot2s3.git
!cd uniprot2s3
!make all
!tar -czvf uniprot_human.tar.gz uniprot2s3/data/raw/s3/*.tsv
```

##### Outputs
- Location: S3
- File: uniprot_human.tar.gz <add link>

#### Step 2: Other Data Download
##### Repository: kg-microbe

This step downloads all other source ingests.

```
!git clone git@github.com:Knowledge-Graph-Hub/kg-microbe.git
!poetry install
!kg download
```

##### Outputs
- Location: S3
- File: kg_microbe_downloads.tar.gz <add link>

#### Step 3: Transform Data
##### Repository: kg-microbe

This step normalizes and models data from each source according to KG structure.

```
!kg transform
```

##### Outputs
- Location: github release
- File: [2024-09-28.tar.gz](https://github.com/Knowledge-Graph-Hub/kg-microbe/archive/refs/tags/2024-09-28.tar.gz)

#### Step 4: Merge Data in Final KGs
##### Repositories: kg-microbe, kg-microbe-merge

This step deduplicates all nodes and edges and outputs graphs in KGX format.

For the two graphs without functional annotation data, KGX merge files with all columns necessary for use with KG-Hub libraries are built using kg-microbe.

##### Repository: kg-microbe

To construct kg-microbe-core:

```
!kg merge
```

##### Outputs
- Location: S3
- File: kg_microbe_core.tar.gz <add link>

To construct kg-microbe-biomedical, the following lines in the merge.yaml must be uncommented: 

```
    # mondo:
    #   name: "MONDO"
    #   input:
    #     format: tsv
    #     filename:
    #       - data/transformed/ontologies/mondo_nodes.tsv
    #       - data/transformed/ontologies/mondo_edges.tsv
    # hp:
    #   name: "HP"
    #   input:
    #     format: tsv
    #     filename:
    #       - data/transformed/ontologies/hp_nodes.tsv
    #       - data/transformed/ontologies/hp_edges.tsv
    
    <...>
    
    
    # ctd:
    #   input:
    #     name: "ctd"
    #     format: tsv
    #     filename:
    #       - data/transformed/ctd/nodes.tsv
    #       - data/transformed/ctd/edges.tsv
    # disbiome:
    #   input:
    #     name: "disbiome"
    #     format: tsv
    #     filename:
    #       - data/transformed/disbiome/nodes.tsv
    #       - data/transformed/disbiome/edges.tsv
    # wallen_etal:
    #   input:
    #     name: "wallen_etal"
    #     format: tsv
    #     filename:
    #       - data/transformed/wallen_etal/nodes.tsv
    #       - data/transformed/wallen_etal/edges.tsv
    # Not feasible using kgx merge process
    # uniprot_functional_microbes:
    #   input:
    #     name: "uniprot_functional_microbes"
    #     format: tsv
    #     filename:
    #       - data/transformed/uniprot_functional_microbes/nodes.tsv
    #       - data/transformed/uniprot_functional_microbes/edges.tsv
    # uniprot_human:
    #   input:
    #     name: "uniprot_human"
    #     format: tsv
    #     filename:
    #       - data/transformed/uniprot_human/nodes.tsv
    #       - data/transformed/uniprot_human/edges.tsv
```

```
!kg merge
```

##### Outputs
- Location: S3
- File: kg_microbe_biomedical.tar.gz <add link>


##### Repository: kg-microbe-merge

```
!git clone git@github.com:Knowledge-Graph-Hub/kg-microbe-merge.git
!poetry install
!kg download
!make datamodel 
```

To construct kg-microbe-function:

```
!make kg-microbe-function
```

##### Outputs
- Location: S3
- File: kg-microbe-function.tar.gz <add link>

To construct kg-microbe-biomedical-function:

```
!make kg-microbe-biomedical-function
```

##### Outputs
- Location: S3
- File: kg-microbe-biomedical-function.tar.gz <add link>