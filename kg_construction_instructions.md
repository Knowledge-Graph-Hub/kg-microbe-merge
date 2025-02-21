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

This step queries the UniProt API for microbial and human functional annotation data. This step is only required to build the following KGs:
- kg-microbe-function
- kg-microbe-biomedical-function

```
git clone git@github.com:Knowledge-Graph-Hub/uniprot2s3.git
cd uniprot2s3
make all
```
##### Outputs
- Location: S3
- File: uniprot_proteomes.tar.gz <add link>

To create the human raw file, the "human_query" branch must be checked out:

```
git checkout human_query
make all
tar -czvf uniprot_human.tar.gz uniprot2s3/data/raw/s3/*.tsv
```

##### Outputs
- Location: S3
- File: uniprot_human.tar.gz <add link>

#### Step 2: Other Data Download
##### Repository: kg-microbe

This step downloads all other source ingests. This step is required to build all KGs:
- kg-microbe-core
- kg-microbe-biomedical
- kg-microbe-function
- kg-microbe-biomedical-function

```
git clone git@github.com:Knowledge-Graph-Hub/kg-microbe.git
cd kg-microbe
poetry install
kg download
```

##### Outputs
- Location: S3
- File: kg_microbe_downloads.tar.gz <add link>

#### Step 3: Transform Data
##### Repository: kg-microbe

This step normalizes and models data from each source according to KG structure. This step is required to build all KGs:
- kg-microbe-core
- kg-microbe-biomedical
- kg-microbe-function
- kg-microbe-biomedical-function

```
kg transform
```

##### Outputs
- Location: GitHub release
- File: [2024-09-28.tar.gz](https://github.com/Knowledge-Graph-Hub/kg-microbe/archive/refs/tags/2024-09-28.tar.gz)

#### Step 4: Merge Data in Final KGs
##### Repositories: kg-microbe, kg-microbe-merge

This step deduplicates all nodes and edges and outputs graphs in KGX format.

For the two graphs without functional annotation data, files are output in full KGX format (KGX merge files with all columns necessary for use with KG-Hub libraries).

##### Repository: kg-microbe

To construct kg-microbe-core:

```
kg merge
```
!!! NEED TO UDPATE CODE TO RENAME THE FOLLOWING FILES FOR CORE AND BIOMEDICAL:
- merged-kg.tar.gz
- merge.yaml
- merged_graph_stats.yaml
!!!

##### Outputs
- Location: GitHub release
- File: kg_microbe_core.tar.gz <add link>

To construct kg-microbe-biomedical, the "biomedical_merge" branch must be checked out:

```
git checkout biomedical_merge
kg merge
```

##### Outputs
- Location: GitHub release
- File: kg_microbe_biomedical.tar.gz <add link>

The next steps are necessary for the following graphs:
- kg-microbe-function
- kg-microbe-biomedical-function

##### Repository: kg-microbe-merge

```
git clone git@github.com:Knowledge-Graph-Hub/kg-microbe-merge.git
poetry install
kg download
```

To construct kg-microbe-function:

```
make kg-microbe-function
```

##### Outputs
- Location: S3
- File: kg-microbe-function.tar.gz <add link>

To construct kg-microbe-biomedical-function:

```
make kg-microbe-biomedical-function
```

##### Outputs
- Location: S3
- File: kg-microbe-biomedical-function.tar.gz <add link>